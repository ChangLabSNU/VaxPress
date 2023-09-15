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

class LongStemFitness(ScoringFunction):

    name = 'longstem'
    description = 'RNA Folding (Long Stems)'
    priority = 43
    uses_folding = True

    arguments = [
        ('weight', dict(metavar='WEIGHT',
            type=float, default=100.0,
            help='penalty score for long stems (default: 100.0)')),
        ('threshold', dict(
            type=int, default=27, metavar='N',
            help='minimum length of stems to avoid (default: 27)')),
    ]

    penalty_metric_flags = {}

    def __init__(self, threshold, weight, _length_cds):
        self.threshold = threshold
        self.weight = -weight

        if weight != 0:
            self.penalty_metric_flags[self.name] = 'l'

    def score(self, seqs, foldings):
        metrics = []
        scores = []

        for fold in foldings:
            stems = fold['stems']
            longstems = sum(len(loc5) >= self.threshold for loc5, _ in stems)
            metrics.append(longstems)
            scores.append(longstems * self.weight)

        return {'longstem': scores}, {'longstem': metrics}

    def annotate_sequence(self, seq, folding):
        longstems = sum(len(loc5) >= self.threshold
                        for loc5, _ in folding['stems'])
        return {'longstems': longstems}
