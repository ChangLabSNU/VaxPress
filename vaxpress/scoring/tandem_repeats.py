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
import pytrf

class TandemRepeatsFitness(ScoringFunction):

    name = 'repeats'
    description = 'Tandem Repeats'
    priority = 60

    arguments = [
        ('weight',
         dict(type=float, default=1.0, metavar='WEIGHT',
              help='scoring weight for tandem repeats (default: 1.0)')),
        ('min-repeats',
         dict(type=int, default=2, metavar='N',
              help='minimum number of repeats to be considered as a tandem '
                   'repeat (default: 2)')),
        ('min-length',
         dict(type=int, default=10, metavar='LENGTH',
              help='minimum length of repeats to be considered as a tandem '
                   'repeat (default: 10)')),
    ]

    penalty_metric_flags = {'repeat': 'r'}

    def __init__(self, weight, min_repeats, min_length, _length_cds):
        self.weight = weight / _length_cds * -1000
        self.min_repeats = min_repeats
        self.min_length = min_length

    def score(self, seqs):
        replengths = []
        for seq in seqs:
            repeats = pytrf.GTRFinder('name', seq, min_repeat=self.min_repeats,
                                    min_length=self.min_length)
            replengths.append(sum(r.length for r in repeats))

        repeat_score = [length * self.weight for length in replengths]

        metrics = {'repeat': replengths}
        scores = {'repeat': repeat_score}

        return scores, metrics
