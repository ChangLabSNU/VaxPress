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
from ..data import bicodon_usage_data
import numpy as np
from itertools import product

class BicodonAdaptationIndexFitness(ScoringFunction):

    name = 'bicodon'
    description = 'Codon Adaptation Index of Codon-Pairs'
    priority = 21

    requires = ['species']
    arguments = [
        ('weight', dict(
            type=float, default=1.0, metavar='WEIGHT',
            help='scoring weight for codon adaptation index of codon-pairs '
                 '(default: 1.0)'
        )),
    ]

    def __init__(self, weight, _length_cds, _species):
        self.weight = weight
        self.species = _species
        self.initialize_bicodon_scores()

    def initialize_bicodon_scores(self):
        if self.species not in bicodon_usage_data.bicodon_usage:
            raise ValueError(f'No bicodon usage data for species: {self.species}')

        bicodon_usage = (
            bicodon_usage_data.bicodon_usage[self.species].astype(np.float64))
        pairs = [''.join(seq) for seq in product('ACGU', repeat=6)]

        self.bicodon_scores = dict(zip(pairs, bicodon_usage))
        assert len(self.bicodon_scores) == 4096

    def score(self, seqs):
        if len(seqs[0]) < 6:
            return [0.0] * len(seqs)

        scores = self.bicodon_scores
        bcai = np.array([
            np.mean([scores[seq[i:i+6]] for i in range(0, len(seq) - 3, 3)])
            for seq in seqs])
        bcai_score = bcai * self.weight

        return {'bicodon': bcai_score}, {'bicodon': bcai}
