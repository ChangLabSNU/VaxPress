#
# VaxPress
#
# Copyright 2024 Seoul National University
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# “Software”), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import asyncio
from aio_pika import Message, connect
from itertools import count
from struct import unpack
import uuid
import numpy as np
import json


class AsyncVaxiFoldClient:

    def __init__(self, url, queue):
        self.url = url
        self.queue = queue

        self.futures = {}
        self.parsers = {}
        self.results = {}

    async def connect(self):
        self.connection = await connect(self.url)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=False)

        return self

    async def on_response(self, message):
        if message.correlation_id is None:
            #log.warning(f'Bad message {message!r}')
            return

        callid, seqid = message.correlation_id.split(':', 1)

        if callid not in self.futures:
            #log.warning(f'Unknown callid {callid!r}')
            return

        result = self.parsers[callid](message.body)
        self.results[callid][1][seqid] = result

        if len(self.results[callid][1]) >= self.results[callid][0]:
            future = self.futures.pop(callid)
            call_results = self.results.pop(callid)[1]
            future.set_result(call_results)
            del self.parsers[callid]

    @staticmethod
    def parse_response_json(response):
        return json.loads(response)

    @staticmethod
    def parse_response_linearpartition(response):
        bp_dtype = [('i', 'i4'), ('j', 'i4'), ('prob', 'f8')]
        free_energy, seqlen = unpack('di', response[:12])
        return {
            'structure': response[12:12+seqlen].decode(),
            'free_energy': free_energy,
            'bpp': np.frombuffer(response[12+seqlen:], dtype=bp_dtype),
        }

    async def call_rpc(self, payloads, parser, loop):
        loop = loop if loop is not None else asyncio.get_running_loop()

        future = loop.create_future()
        callid = uuid.uuid4().hex

        self.futures[callid] = future
        self.parsers[callid] = parser
        self.results[callid] = len(payloads), {}

        for seqid, payload in payloads.items():
            message = Message(
                payload, reply_to=self.callback_queue.name,
                correlation_id=f'{callid}:{seqid}'
            )

            await self.channel.default_exchange.publish(
                message, routing_key=self.queue)

        return await future

    def call_viennarna_fold(self, seqs, loop=None):
        payloads = {
            key: json.dumps({'method': 'viennarna_fold', 'args': {'seq': seq}}).encode()
            for key, seq in seqs.items()
        }
        return self.call_rpc(payloads, self.parse_response_json, loop)

    def call_linearfold(self, seqs, loop=None):
        payloads = {
            key: json.dumps({'method': 'linearfold', 'args': {'seq': seq}}).encode()
            for key, seq in seqs.items()
        }
        return self.call_rpc(payloads, self.parse_response_json, loop)

    def call_linearpartition(self, seqs, loop=None):
        payloads = {
            key: json.dumps({'method': 'linearpartition', 'args': {'seq': seq}}).encode()
            for key, seq in seqs.items()
        }
        return self.call_rpc(payloads, self.parse_response_linearpartition, loop)


def run_viennarna_fold(seq):
    import RNA
    structure, mfe = RNA.fold(seq)
    return {
        'structure': structure,
        'free_energy': mfe,
    }

def run_linearfold(seq):
    import linearfold
    structure, mfe = linearfold.fold(seq)
    return {
        'structure': structure,
        'free_energy': mfe,
    }

def run_linearpartition(seq):
    import linearpartition
    return linearpartition.partition(seq)


class LocalFoldingBroker:

    def __init__(self, executor):
        self.executor = executor

        self.callid_pool = count()

        self.futures = {}
        self.results = {}

    async def fold(self, func, seqs, loop):
        loop = loop if loop is not None else asyncio.get_running_loop()

        future = loop.create_future()
        callid = next(self.callid_pool)

        self.futures[callid] = future
        self.results[callid] = len(seqs), {}

        for seqid, seq in seqs.items():
            job = loop.run_in_executor(self.executor, func, seq)
            job._seqid = seqid
            job._callid = callid
            job.add_done_callback(self.on_fold_done)

        return await future

    def on_fold_done(self, job):
        callid = job._callid
        seqid = job._seqid
        result = job.result()

        self.results[callid][1][seqid] = result

        if len(self.results[callid][1]) >= self.results[callid][0]:
            future = self.futures.pop(callid)
            call_results = self.results.pop(callid)[1]
            future.set_result(call_results)

    def call_viennarna_fold(self, seqs, loop=None):
        return self.fold(run_viennarna_fold, seqs, loop)

    def call_linearfold(self, seqs, loop=None):
        return self.fold(run_linearfold, seqs, loop)

    def call_linearpartition(self, seqs, loop=None):
        return self.fold(run_linearpartition, seqs, loop)


class FoldingManager:

    def __init__(self, sess, executor):
        self.sess = sess
        self.executor = executor

    async def initialize(self):
        mfe_engine = self.sess['folding/mfe-engine']
        partition_engine = self.sess['folding/partition-engine']

        if mfe_engine.startswith('vaxifold/') or partition_engine.startswith('vaxifold/'):
            await self.initialize_vaxifold()

        if not mfe_engine.startswith('vaxifold/') or not partition_engine.startswith('vaxifold/'):
            self.initialize_local_broker()

        self.initialize_mfe_engine()
        self.initialize_partition_engine()

        return self

    def initialize_vaxifold(self):
        self.vaxiclient = AsyncVaxiFoldClient(self.sess['folding/vaxifold/url'],
                                              self.sess['folding/vaxifold/queue'])
        return self.vaxiclient.connect()

    def initialize_local_broker(self):
        self.local = LocalFoldingBroker(self.executor)

    def initialize_mfe_engine(self):
        engine = self.sess['folding/mfe-engine']
        if engine == 'viennarna':
            self.predict_mfe = self.local.call_viennarna_fold
        elif engine == 'linearfold':
            self.predict_mfe = self.local.call_linearfold
        elif engine == 'vaxifold/viennarna':
            self.predict_mfe = self.vaxiclient.call_viennarna_fold
        elif engine == 'vaxifold/linearfold':
            self.predict_mfe = self.vaxiclient.call_linearfold
        else:
            raise ValueError(f'Unknown MFE engine {engine!r}')

    def initialize_partition_engine(self):
        engine = self.sess['folding/partition-engine']
        if engine == 'linearpartition':
            self.predict_partition = self.local.call_linearpartition
        elif engine == 'vaxifold/linearpartition':
            self.predict_partition = self.vaxiclient.call_linearpartition
        else:
            raise ValueError(f'Unknown partition engine {engine!r}')
