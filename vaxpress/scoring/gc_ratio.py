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
import numpy as np

def gc_content_sliding_window(seq, winsize, stride):
    chars = np.frombuffer(seq.encode(), dtype=np.uint8)
    isgc = ((chars == ord('G')) + (chars == ord('C')))
    gc = []
    for i in range(0, len(chars) - winsize + 1, stride):
        gc.append(np.mean(isgc[i:i+winsize]))
    return np.array(gc)

def compute_gc_penalty(seq, winsize, stride):
    gc = gc_content_sliding_window(seq, winsize, stride)
    return -(10 ** np.log2(np.abs(gc - 0.5) + 0.1)).sum()

class GCRatioFitness(ScoringFunction):

    single_submission = False

    name = 'gc'
    description = 'GC Ratio'
    priority = 50

    arguments = [
        ('weight', dict(
            type=float, default=3.0, metavar='WEIGHT',
            help='scoring weight for GC ratio (default: 3.0)')),
        ('window-size', dict(
            type=int, default=50, metavar='SIZE',
            help='size of window for GC content calculation (default: 50)')),
        ('stride', dict(
            type=int, default=5, metavar='STRIDE',
            help='size of stride for GC content calculation (default: 5)')),
    ]

    def __init__(self, weight, window_size, stride, _length_cds):
        num_windows = (_length_cds - window_size) // stride + 1
        num_windows = max(num_windows, 1)

        self.weight = weight / num_windows
        self.window_size = window_size
        self.stride = stride

    def score(self, seqs):
        gc_penalties = [compute_gc_penalty(seq, self.window_size, self.stride)
                        for seq in seqs]
        scores = [s * self.weight for s in gc_penalties]
        return {'gc_penalty': scores}, {'gc_penalty': gc_penalties}

    def evaluate_local(self, seq):
        gc = gc_content_sliding_window(seq, self.window_size, self.stride)
        centers = (
            np.arange(0, len(seq) - self.window_size + 1, self.stride) +
            self.window_size / 2)
        return {'gc': (centers, gc)}
