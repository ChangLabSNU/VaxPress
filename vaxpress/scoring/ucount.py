#
# VaxPress
#
# Copyright 2023 Hyeshik Chang
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

class UridineCountFitness(ScoringFunction):

    single_submission = False

    name = 'ucount'
    description = 'Uridines'
    priority = 30

    arguments = [
        ('weight',
         dict(type=float, default=3.0, metavar='WEIGHT',
              help='scoring weight for U count minimizer (default: 3.0)')),
    ]

    def __init__(self, weight, _length_cds):
        self.weight = -weight / _length_cds * 4

    def score(self, seqs):
        ucounts = [s.count('U') for s in seqs]
        scores = [s * self.weight for s in ucounts]
        return {'ucount': scores}, {'ucount': ucounts}
