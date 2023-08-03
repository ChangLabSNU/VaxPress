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

class RNAFoldingFitness(ScoringFunction):

    single_submission = True

    name = 'folding'

    def __init__(self, engine, mfe_weight,
                 start_structure_width, start_structure_weight,
                 length_cds, off=False):
        # off is handled by CDSEvolutionChamber.initialize_fitness_scorefuncs()
        self.mfe_weight = -mfe_weight / length_cds
        self.start_structure_width = start_structure_width
        self.start_structure_weight = -start_structure_weight
        self.engine = engine

        if engine == 'vienna':
            import RNA
            self.fold = RNA.fold
        elif engine == 'linearfold':
            try:
                from vaxpress import linearfold
            except ImportError:
                raise ImportError('VaxPress is not installed with LinearFold '
                                  'support. Try installing a non-free package.')
            self.fold = linearfold.fold
        else:
            raise ValueError(f'Unsupported RNA folding engine: {engine}')

    def __call__(self, seq):
        folding, mfe = self.fold(seq)

        # folded start codon
        start_structure = folding[:self.start_structure_width]
        start_folded = start_structure.count('(') + start_structure.count(')')

        metrics = {'mfe': mfe, 'start_str': start_folded}
        scores = {'mfe': mfe * self.mfe_weight,
                  'start_str': start_folded * self.start_structure_weight}

        return scores, metrics
