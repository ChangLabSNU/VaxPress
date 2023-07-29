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

from Bio.Data import CodonTable
from collections import namedtuple
import pandas as pd
import numpy as np

STOP = '*'
MutationChoice = namedtuple('MutationChoice', ['pos', 'altcodon'])

class MutantGenerator:

    cdsseq = None
    initial_codons = None

    def __init__(self, cdsseq: str, random_state: np.random.RandomState,
                 codon_table: str='standard'):
        self.initialize_codon_table(codon_table)

        self.cdsseq = cdsseq
        if len(self.cdsseq) % 3 != 0:
            raise ValueError('Invalid CDS sequence length')

        self.rand = np.random if random_state is None else random_state

        self.setup_choices()

    def initialize_codon_table(self, codon_table: str) -> None:
        table_var_name = f'{codon_table}_rna_table'
        if not hasattr(CodonTable, table_var_name):
            raise ValueError(f'Invalid codon table name: {codon_table}')

        self.codon_table = getattr(CodonTable, table_var_name)

        tbl = pd.DataFrame(
            list(self.codon_table.forward_table.items()) +
            [[stopcodon, STOP] for stopcodon in self.codon_table.stop_codons],
            columns=['codon', 'aa'])

        # Build synonymous codon lookup table
        self.synonymous_codons, self.aa2codons, self.codon2aa = {}, {}, {}
        for aa, codons in tbl.groupby('aa'):
            codons = set(codons['codon'])
            self.aa2codons[aa] = codons
            for c in codons:
                self.synonymous_codons[c] = sorted(codons - set([c]))
                self.codon2aa[c] = aa

    def setup_choices(self) -> None:
        choices = []
        initial_codons = []

        for i in range(len(self.cdsseq) // 3):
            codon = self.cdsseq[i*3:i*3+3]
            alternatives = len(self.synonymous_codons[codon])
            for alt in range(alternatives):
                choices.append(MutationChoice(i, alt))
            initial_codons.append(codon)

        self.choices = choices
        self.initial_codons = initial_codons

    def generate_mutant(self, codons: list[str],
                        mutation_rate: float) -> list[str]:
        child = codons[:]

        # Draw number of mutations from binomial distribution
        n_mutations = self.rand.binomial(len(self.choices), mutation_rate)
        n_mutations = max(1, min(n_mutations, len(self.choices)))

        # Select mutations
        mutation_choices = self.rand.choice(len(self.choices),
                                            n_mutations, replace=False)

        # Apply mutations
        for i in mutation_choices:
            mut = self.choices[i]
            child[mut.pos] = self.synonymous_codons[child[mut.pos]][mut.altcodon]

        return child

    def generate_mutants(self, parent: list[str], n_progeny: int,
                         mutation_rate: float) -> list[list[str]]:
        return [self.generate_mutant(parent, mutation_rate)
                for i in range(n_progeny)]

    def compute_expected_mutations(self, mutation_rate: float) -> float:
        return len(self.choices) * mutation_rate

    def compute_mutational_space(self) -> dict:
        log10_totalcases = np.sum(np.log10(list((map(len, self.choices)))))
        totalcases_mantissa = 10 ** (log10_totalcases % 1)
        totalcases = f'{totalcases_mantissa:.2f} x 10^{int(log10_totalcases)}'

        return {
            'singles': len(self.choices),
            'total': totalcases,
        }

if __name__ == '__main__':
    rand = np.random.RandomState(922)
    mg = MutantGenerator('AUGCCUGAUUUUACGAUGUAA', rand, 'standard')
    current = mg.initial_codons
    print(current)
    new = mg.generate_mutants(current, 10, 0.1)
    print(new)
