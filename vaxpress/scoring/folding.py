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
import re

def find_stems(structure):
    stack = []
    stemgroups = []

    for i, s in enumerate(structure):
        if s == '(':
            stack.append(i)
        elif s == ')':
            assert len(stack) >= 1
            peer = stack.pop()
            if (stemgroups and peer + 1 == stemgroups[-1][0][-1] and
                    i - 1 == stemgroups[-1][1][-1]):
                stemgroups[-1][0].append(peer)
                stemgroups[-1][1].append(i)
            else:
                stemgroups.append(([peer], [i]))

    return stemgroups

class RNAFoldingFitness(ScoringFunction):

    single_submission = True

    name = 'folding'
    description = 'RNA Folding'
    priority = 40

    arguments = [
        ('off', dict(
            action='store_true', default=False,
            help='disable secondary structure folding')),
        ('engine', dict(
            choices=['vienna', 'linearfold'], default='vienna',
            metavar='NAME', help='RNA folding engine (default: vienna)')),
        ('mfe-weight', dict(
            type=float, default=3.0, metavar='WEIGHT',
            help='scoring weight for MFE (default: 3.0)')),
        ('start-structure-width', dict(
            type=int, default=15, metavar='WIDTH',
            help='width in nt of unfolded region near the start codon (default: 15)')),
        ('start-structure-weight', dict(
            type=int, default=1, metavar='WEIGHT',
            help='penalty weight for folded start codon region (default: 1)')),
        ('loop-threshold', dict(
            type=int, default=2, metavar='N',
            help='minimum count of unfolded bases to be considered as a loop '
                 '(default: 2)')),
        ('loop-weight', dict(metavar='WEIGHT',
            type=float, default=1.5, help='scoring weight for loops (default: 1.5)')),
        ('longstem-threshold', dict(
            type=int, default=27, metavar='N',
            help='minimum length of stems to avoid (default: 27)')),
        ('longstem-weight', dict(metavar='WEIGHT',
            type=float, default=100.0,
            help='penalty score for long stems (default: 100.0)')),
    ]

    penalty_metric_flags = {}

    def __init__(self, engine, mfe_weight,
                 start_structure_width, start_structure_weight,
                 loop_threshold, loop_weight,
                 longstem_threshold, longstem_weight,
                 _length_cds, off=False):
        # `off' is handled by CDSEvolutionChamber.initialize_fitness_scorefuncs()

        self.mfe_weight = -mfe_weight / _length_cds
        self.start_structure_width = start_structure_width
        self.start_structure_weight = -start_structure_weight
        self.loop_threshold = loop_threshold
        self.loop_weight = -loop_weight / _length_cds
        self.longstem_threshold = longstem_threshold
        self.longstem_weight = -longstem_weight
        self.engine = engine

        if engine == 'vienna':
            import RNA
            self.fold = RNA.fold
        elif engine == 'linearfold':
            try:
                import linearfold
            except ImportError:
                raise ImportError('LinearFold module is not available. Try "'
                                  'pip install linearfold-unofficial" to install.')
            self.fold = linearfold.fold
        else:
            raise ValueError(f'Unsupported RNA folding engine: {engine}')

        if loop_weight != 0 and loop_threshold >= 1:
            self.find_loops = re.compile('\\.{' + str(loop_threshold) + ',}')
        else:
            self.find_loops = None

        if longstem_weight != 0:
            self.penalty_metric_flags['longstem'] = 'l'

        if start_structure_weight != 0:
            self.penalty_metric_flags['start_str'] = 's'

    def score(self, seq):
        folding, mfe = self.fold(seq)

        # folded start codon
        start_structure = folding[:self.start_structure_width]

        metrics, scores = {}, {}

        if self.mfe_weight != 0:
            metrics['mfe'] = mfe
            scores['mfe'] = mfe * self.mfe_weight

        if self.start_structure_weight != 0:
            start_folded = start_structure.count('(') + start_structure.count(')')
            metrics['start_str'] = start_folded
            scores['start_str'] = start_folded * self.start_structure_weight

        if self.find_loops is not None:
            loops = sum(map(len, self.find_loops.findall(folding)))
            metrics['loop'] = loops
            scores['loop'] = loops * self.loop_weight

        if self.longstem_weight != 0:
            stems = find_stems(folding)
            longstems = sum(len(loc5) >= self.longstem_threshold
                            for loc5, _ in stems)
            metrics['longstem'] = longstems
            scores['longstem'] = longstems * self.longstem_weight

        return scores, metrics

    def annotate_sequence(self, seq):
        folding, mfe = self.fold(seq)

        anno = {'folding': folding, 'mfe': mfe}
        if self.find_loops is not None:
            loops = sum(map(len, self.find_loops.findall(folding)))
            anno['loops'] = loops

        if self.longstem_weight != 0:
            stems = find_stems(folding)
            longstems = sum(len(loc5) >= self.longstem_threshold
                            for loc5, _ in stems)
            anno['longstems'] = longstems

        return anno
