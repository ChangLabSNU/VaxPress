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

from . import ScoringFunction
from ..datacache import get_cachepath
from ..log import log
import importlib.util as imputil
import sys


class LazyLoadingDegScoreProxy:

    DEGSCORE_RAW_PREFIX = 'https://raw.githubusercontent.com/eternagame/DegScore/master/'
    download_addresses = {
        'DegScore.py': f'{DEGSCORE_RAW_PREFIX}DegScore.py',
        'assign_loop_type.py': f'{DEGSCORE_RAW_PREFIX}assign_loop_type.py',
    }

    def __init__(self):
        self.module = None

    def __call__(self, seq, fold):
        if self.module is None:
            self.load_module()

        mdl = self.module.DegScore(seq, structure=fold)
        return mdl.degscore / len(seq)

    def score_by_position(self, seq, fold):
        if self.module is None:
            self.load_module()

        mdl = self.module.DegScore(seq, structure=fold)
        return mdl.degscore_by_position

    def load_module(self):
        try:
            for fn in self.download_addresses:
                open(get_cachepath(fn))
        except FileNotFoundError:
            self.download_module()

        for mod in ['assign_loop_type', 'DegScore']:
            spec = imputil.spec_from_file_location(mod, get_cachepath(mod + '.py'))
            module = imputil.module_from_spec(spec)
            sys.modules[mod] = module
            module.print = lambda *args, **kwargs: None
            spec.loader.exec_module(module)

        self.module = sys.modules['DegScore']

    # This method might need a locking mechanism in the future. Currently,
    # it is not a problem because the first call is made only during the
    # generation of the intermediate report for the first iteration in the main
    # process.
    def download_module(self):
        import urllib.request
        import os

        datadir = get_cachepath('.')
        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        for filename, url in self.download_addresses.items():
            cachepath = get_cachepath(filename)
            log.info(f'==> Downloading a DegScore file from {url} to {cachepath}')
            urllib.request.urlretrieve(url, cachepath)

call_degscore = LazyLoadingDegScoreProxy()


class DegScoreFitness(ScoringFunction):

    name = 'degscore'
    description = 'DegScore (Eterna Predicted Degradation Rate)'
    priority = 15
    uses_folding = True

    arguments = [
        ('weight',
         dict(type=float, default=0, metavar='WEIGHT',
              help='scoring weight for DegScore. (default: 0)')),
    ]

    def __init__(self, weight, _length_cds):
        self.weight = -weight

    def score(self, seqs, foldings):
        degscores = [call_degscore(seq, fold['folding'])
                     for seq, fold in zip(seqs, foldings)]
        weighted_scores = [s * self.weight for s in degscores]
        return {'degscore': weighted_scores}, {'degscore': degscores}

    def annotate_sequence(self, seq, folding):
        degscore = call_degscore(seq, folding['folding'])
        return {'degscore': degscore}

    def evaluate_local(self, seq, folding):
        degscore = call_degscore.score_by_position(seq, folding['folding'])
        baseindex = list(range(len(seq)))
        return {'degscore': (baseindex, degscore)}
