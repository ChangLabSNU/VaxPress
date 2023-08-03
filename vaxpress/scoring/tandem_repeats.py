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
import pytrf

class TandemRepeatsFitness(ScoringFunction):

    single_submission = True

    name = 'repeats'

    def __init__(self, weight, min_repeats, repeat_length, length_cds, species):
        self.weight = weight / length_cds * -1000
        self.min_repeats = min_repeats
        self.repeat_length = repeat_length

    def __call__(self, seq):
        repeats = pytrf.GTRFinder('name', seq, min_repeat=self.min_repeats,
                                min_length=self.repeat_length)
        total_repeat_length = sum(r.length for r in repeats)
        repeat_score = total_repeat_length * self.weight

        metrics = {'repeat': total_repeat_length}
        scores = {'repeat': repeat_score}

        return scores, metrics
