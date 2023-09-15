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
from ..data import codon_usage_data
import numpy as np

class CodonAdaptationIndexFitness(ScoringFunction):

    name = 'cai'
    description = 'Codon Adaptation Index'
    priority = 20

    use_annotation_on_zero_weight = True

    requires = ['mutantgen', 'species']
    arguments = [
        ('weight', dict(
            type=float, default=0, metavar='WEIGHT',
            help='scoring weight for codon adaptation index (default: 0)'
        )),
    ]

    def __init__(self, weight, _length_cds, _species, _mutantgen):
        self.weight = weight
        self.species = _species
        self.mutantgen = _mutantgen
        self.initialize_codon_scores()

    def initialize_codon_scores(self):
        if self.species not in codon_usage_data.codon_usage:
            raise ValueError(f'No codon usage data for species: {self.species}')

        codon_usage = codon_usage_data.codon_usage[self.species]
        scores = {}
        for aa, codons in self.mutantgen.aa2codons.items():
            codons = sorted(codons)
            freqs = np.array([codon_usage[c] for c in codons])
            scores.update(dict(zip(codons, np.log(freqs / freqs.max()))))

        self.codon_scores = scores

    def score(self, seqs):
        scores = self.codon_scores
        cai = np.array([
            np.mean([scores[seq[i:i+3]] for i in range(0, len(seq), 3)])
            for seq in seqs])
        cai_score = cai * self.weight

        return {'cai': cai_score}, {'cai': cai}

    def evaluate_local(self, seq):
        scores = self.codon_scores
        cai = np.array([scores[seq[i:i+3]] for i in range(0, len(seq), 3)])
        centers = np.arange(0, len(seq), 3) + 1
        return {'cai': (centers, cai)}
