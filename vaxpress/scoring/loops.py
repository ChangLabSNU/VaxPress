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

class LoopLengthFitness(ScoringFunction):

    name = 'loop'
    description = 'RNA Folding (Loops)'
    priority = 41
    uses_folding = True

    arguments = [
        ('weight', dict(metavar='WEIGHT',
            type=float, default=1.5, help='scoring weight for loops (default: 1.5)')),
        ('threshold', dict(
            type=int, default=2, metavar='N',
            help='minimum count of unfolded bases to be considered as a loop '
                 '(default: 2)')),
    ]

    def __init__(self, threshold, weight, _length_cds):
        self.threshold = threshold
        self.weight = -weight / _length_cds

    def score(self, seqs, foldings):
        loop_lengths = []
        scores = []
        for fold in foldings:
            looplen = sum(length * count
                          for length, count in fold['loops'].items()
                          if length >= self.threshold)
            loop_lengths.append(looplen)
            scores.append(looplen * self.weight)

        return {'loop': scores}, {'loop': loop_lengths}

    def annotate_sequence(self, seq, folding):
        looplen = sum(length * count
                      for length, count in folding['loops'].items()
                      if length >= self.threshold)
        return {'loop': looplen}
