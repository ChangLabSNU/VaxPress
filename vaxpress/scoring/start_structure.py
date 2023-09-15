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

class StartCodonStructureFitness(ScoringFunction):

    name = 'start_str'
    description = 'RNA Folding (Structure near Start Codon)'
    priority = 42
    uses_folding = True

    arguments = [
        ('weight', dict(
            type=int, default=1, metavar='WEIGHT',
            help='penalty weight for folded start codon region (default: 1)')),
        ('width', dict(
            type=int, default=15, metavar='WIDTH',
            help='width in nt of unfolded region near the start codon (default: 15)')),
    ]

    penalty_metric_flags = {}

    def __init__(self, width, weight, _length_cds):
        self.width = width
        self.weight = -weight

        if weight != 0:
            self.penalty_metric_flags[self.name] = 's'

    def score(self, seqs, foldings):
        metrics = []
        scores = []

        for fold in foldings:
            start_structure = fold['folding'][:self.width]

            start_folded = start_structure.count('(') + start_structure.count(')')
            metrics.append(start_folded)
            scores.append(start_folded * self.weight)

        return {'start_str': scores}, {'start_str': metrics}

    def annotate_sequence(self, seq, folding):
        start_structure = folding['folding'][:self.width]
        start_folded = start_structure.count('(') + start_structure.count(')')
        return {'start_str': start_folded}
