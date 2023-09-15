#
# VaxPress
#
# Copyright 2023 Seoul National University
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

import sys
import re
import pylru
from tqdm import tqdm
from concurrent import futures
from collections import Counter
from .log import hbar_stars, log


class FoldEvaluator:

    def __init__(self, engine: str):
        self.engine = engine
        self.pat_find_loops = re.compile(r'\.{2,}')
        self.initialize()

    def initialize(self):
        if self.engine == 'vienna':
            try:
                import RNA
            except ImportError:
                raise ImportError('ViennaRNA module is not available. Try "'
                                  'pip install ViennaRNA" to install.')
            self._fold = RNA.fold
        elif self.engine == 'linearfold':
            try:
                import linearfold
            except ImportError:
                raise ImportError('LinearFold module is not available. Try "'
                                  'pip install linearfold-unofficial" to install.')
            self._fold = linearfold.fold
        else:
            raise ValueError(f'Unsupported RNA folding engine: {self.engine}')

    def __call__(self, seq):
        folding, mfe = self._fold(seq)
        stems = self.find_stems(folding)
        folding, stems = self.unfold_unstable_structure(folding, stems)
        loops = dict(Counter(map(len, self.pat_find_loops.findall(folding))))

        return {
            'folding': folding,
            'mfe': mfe,
            'stems': stems,
            'loops': loops,
        }

    @staticmethod
    def find_stems(structure):
        stack = []
        stemgroups = []

        for i, s in enumerate(structure):
            if s == '(':
                stack.append(i)
            elif s == ')':
                assert len(stack) >= 1
                peer = stack.pop()
                if (stemgroups and peer + 1 == stemgroups[-1][0][-1] and
                        i - 1 == stemgroups[-1][1][-1]):
                    stemgroups[-1][0].append(peer)
                    stemgroups[-1][1].append(i)
                else:
                    stemgroups.append(([peer], [i]))

        return stemgroups

    @staticmethod
    def unfold_unstable_structure(folding, stems):
        # TODO: This needs to be revised based on the thermodynamic model of RNA
        # folding later.
        lonepairs = [p for p in stems if len(p[0]) == 1]
        if not lonepairs:
            return folding, stems

        folding = list(folding)
        for p5, p3 in lonepairs:
            folding[p5[0]] = '.'
            folding[p3[0]] = '.'
        newstems = [p for p in stems if len(p[0]) > 1]

        return ''.join(folding), newstems


class SequenceEvaluator:

    folding_cache_size = 8192

    def __init__(self, scoring_funcs, scoreopts, execopts, mutantgen, species,
                 length_cds, quiet):
        self.scoring_funcs = scoring_funcs
        self.scoreopts = scoreopts
        self.execopts = execopts

        self.length_cds = length_cds
        self.mutantgen = mutantgen
        self.species = species

        self.quiet = quiet

        self.initialize()

    def initialize(self):
        self.foldeval = FoldEvaluator(self.execopts.folding_engine)
        self.folding_cache = pylru.lrucache(self.folding_cache_size)

        self.scorefuncs_nofolding = []
        self.scorefuncs_folding = []
        self.annotationfuncs = []
        self.penalty_metric_flags = {}

        additional_opts = {
            '_length_cds': self.length_cds,
        }

        for funcname, cls in self.scoring_funcs.items():
            funcoff = False
            opts = self.scoreopts[funcname]
            if (('weight' in opts and opts['weight'] == 0) or
                    ('off' in opts and opts['off'])):
                if not cls.use_annotation_on_zero_weight:
                    continue
                funcoff = True

            opts.update(additional_opts)
            for reqattr in cls.requires:
                opts['_' + reqattr] = getattr(self, reqattr)

            try:
                scorefunc_inst = cls(**opts)
            except EOFError:
                continue

            self.annotationfuncs.append(scorefunc_inst)
            if funcoff:
                continue

            if cls.uses_folding:
                self.scorefuncs_folding.append(scorefunc_inst)
            else:
                self.scorefuncs_nofolding.append(scorefunc_inst)

            self.penalty_metric_flags.update(cls.penalty_metric_flags)

    def evaluate(self, seqs, executor):
        with SequenceEvaluationSession(self, seqs, executor) as sess:
            sess.evaluate()

            if not sess.errors:
                total_scores = [sum(s.values()) for s in sess.scores]
                return total_scores, sess.scores, sess.metrics, sess.foldings
            else:
                return None, None, None, None

    def get_folding(self, seq):
        if seq not in self.folding_cache:
            self.folding_cache[seq] = self.foldeval(seq)
        return self.folding_cache[seq]

    def prepare_evaluation_data(self, seq):
        folding = self.get_folding(seq)

        seqevals = {}
        seqevals['local-metrics'] = localmet = {}
        for fun in self.annotationfuncs:
            if hasattr(fun, 'evaluate_local'):
                if fun.uses_folding:
                    localmet.update(fun.evaluate_local(seq, folding))
                else:
                    localmet.update(fun.evaluate_local(seq))

            if hasattr(fun, 'annotate_sequence'):
                if fun.uses_folding:
                    seqevals.update(fun.annotate_sequence(seq, folding))
                else:
                    seqevals.update(fun.annotate_sequence(seq))

        return seqevals


class SequenceEvaluationSession:

    def __init__(self, evaluator: SequenceEvaluator, seqs: list[str],
                 executor: futures.Executor):
        self.seqs = seqs
        self.executor = executor

        self.scores = [{} for i in range(len(seqs))]
        self.metrics = [{} for i in range(len(seqs))]
        self.foldings = [None] * len(seqs)
        self.errors = []

        self.folding_cache = evaluator.folding_cache
        self.foldings_remaining = len(seqs)
        self.foldeval = evaluator.foldeval

        self.num_tasks = (
            len(evaluator.scorefuncs_folding) +
            len(evaluator.scorefuncs_nofolding) +
            len(seqs))

        self.pbar = None
        self.quiet = evaluator.quiet

        self.scorefuncs_folding = evaluator.scorefuncs_folding
        self.scorefuncs_nofolding = evaluator.scorefuncs_nofolding
        self.annotationfuncs = evaluator.annotationfuncs
    
    def __enter__(self):
        log.info('')
        self.pbar = tqdm(total=self.num_tasks, disable=self.quiet,
                         file=sys.stderr, unit='task', desc='Scoring fitness')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.pbar is not None:
            self.pbar.close()
        log.info('')

    def evaluate(self) -> None:
        jobs = set()

        # Secondary structure prediction is the first set of tasks.
        for i, seq in enumerate(self.seqs):
            if self.errors: # skip remaining tasks on error
                continue

            if seq in self.folding_cache:
                self.foldings[i] = self.folding_cache[seq]
                self.foldings_remaining -= 1
                if self.pbar is not None:
                    self.pbar.update()
                continue

            future = self.executor.submit(self.foldeval, seq)
            future._seqidx = i
            future._type = 'folding'
            jobs.add(future)

        # Then, scoring functions that does not require folding are executed.
        for scorefunc in self.scorefuncs_nofolding:
            if self.errors:
                continue

            future = self.executor.submit(scorefunc, self.seqs)
            future._type = 'scoring'
            jobs.add(future)

        # Wait until all folding tasks are finished.
        while jobs and not self.errors and self.foldings_remaining > 0:
            done, jobs = futures.wait(jobs, timeout=0.1,
                                      return_when=futures.FIRST_COMPLETED)
            for future in done:
                if future._type == 'folding':
                    self.collect_folding(future)
                elif future._type == 'scoring':
                    self.collect_scores(future)

        # Scoring functions requiring folding are executed.
        for scorefunc in self.scorefuncs_folding:
            if self.errors:
                continue

            future = self.executor.submit(scorefunc, self.seqs,
                                          self.foldings)
            future._type = 'scoring'
            jobs.add(future)

        while jobs and not self.errors:
            done, jobs = futures.wait(jobs, timeout=0.1)
            for future in done:
                if future._type == 'folding':
                    self.collect_folding(future)
                elif future._type == 'scoring':
                    self.collect_scores(future)

    def collect_scores(self, future):
        try:
            ret = future.result()
            if ret is None:
                self.errors.append('KeyboardInterrupt')
                if self.pbar is not None:
                    self.pbar.close()
                self.pbar = None
                return
            scoreupdates, metricupdates = ret
        except Exception as exc:
            return self.handle_exception(exc)

        if self.pbar is not None:
            self.pbar.update()

        # Update scores
        for k, updates in scoreupdates.items():
            assert len(updates) == len(self.scores)
            for s, u in zip(self.scores, updates):
                s[k] = u

        # Update metrics
        for k, updates in metricupdates.items():
            assert len(updates) == len(self.metrics)
            for s, u in zip(self.metrics, updates):
                s[k] = u

    def collect_folding(self, future):
        try:
            folding = future.result()
            if folding is None:
                self.errors.append('KeyboardInterrupt')
                if self.pbar is not None:
                    self.pbar.close()
                self.pbar = None
                return
        except Exception as exc:
            return self.handle_exception(exc)
        i = future._seqidx
        self.foldings[i] = folding
        self.folding_cache[self.seqs[i]] = folding
        self.foldings_remaining -= 1

        if self.pbar is not None:
            self.pbar.update()

    def handle_exception(self, exc):
        import traceback
        import io

        errormsg = io.StringIO()
        traceback.print_exc(file=errormsg)

        msg = [
            hbar_stars,
            'Error occurred in a scoring function:',
            errormsg.getvalue(),
            hbar_stars,
            '',
            'Termination in progress. Waiting for running tasks '
            'to finish before closing the program.']

        log.error('\n'.join(msg))
        self.errors.append(exc.args)
