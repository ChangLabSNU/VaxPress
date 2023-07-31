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

from .evolution_chamber import CDSEvolutionChamber, ScoringOptions, IterationOptions
from Bio import SeqIO
import argparse

def parse_options():
    parser = argparse.ArgumentParser(
        prog='vaxpress',
        description='VaxPress: A Codon Optimizer for mRNA Vaccine Design')

    grp = parser.add_argument_group('Input/Output Options')
    grp.add_argument('-o', '--output', required=True, help='output file')
    grp.add_argument('-q', '--quiet', default=False, action='store_true', help='do not print progress')
    grp.add_argument('--print-top', type=int, default=10, help='print top and bottom N sequences (default: 10)')

    grp = parser.add_argument_group('Execution Options')
    grp.add_argument('--seed', type=int, default=922, help='random seed (default: 922)')
    grp.add_argument('-p', '--processes', type=int, default=4, help='number of processes to use (default: 4)')

    grp = parser.add_argument_group('Sequence Options')
    grp.add_argument('--codon-table', default='standard', help='codon table (default: standard)')
    grp.add_argument('--random-initialization', default=False, action='store_true', help='randomize all codons at the beginning')

    grp = parser.add_argument_group('Optimization Options')
    grp.add_argument('--iterations', type=int, default=50, help='number of iterations (default: 50)')
    grp.add_argument('--offsprings', type=int, default=100, help='number of offsprings per iteration (default: 100)')
    grp.add_argument('--survivors', type=int, default=3, help='number of survivors per iteration (default: 3)')
    grp.add_argument('--initial-mutation-rate', type=float, default=0.1, help='initial mutation rate (default: 0.1)')
    grp.add_argument('--winddown-trigger', type=int, default=15, help='number of iterations with the same best score to trigger mutation stabilization (default: 15)')
    grp.add_argument('--winddown-rate', type=float, default=0.9, help='mutation rate multiplier when mutation stabilization is triggered (default: 0.9)')

    grp = parser.add_argument_group('Fitness - iCodon')
    grp.add_argument('--icodon-species', default='human', help='iCodon RNA stability optimizer: species (default: human)')
    grp.add_argument('--icodon-weight', type=float, default=1.0, help='scoring weight for iCodon predicted stability (default: 1.0)')

    grp = parser.add_argument_group('Fitness - Uridines')
    grp.add_argument('--ucount-weight', type=float, default=3.0, help='scoring weight for U count minimizer (default: 3.0)')

    grp = parser.add_argument_group('Fitness - GC Ratio')
    grp.add_argument('--gc-window-size', type=int, default=50, help='size of window for GC content calculation (default: 50)')
    grp.add_argument('--gc-stride', type=int, default=5, help='size of stride for GC content calculation (default: 5)')
    grp.add_argument('--gc-weight', type=int, default=3, help='GC penalty score (default: 3)')

    grp = parser.add_argument_group('Fitness - RNA Folding')
    grp.add_argument('--folding-off', default=False, action='store_true', help='disable secondary structure folding')
    grp.add_argument('--folding-engine', default='vienna', choices=['vienna', 'linearfold'],
                     help='RNA folding engine: vienna (default) or linearfold')
    grp.add_argument('--folding-mfe-weight', type=float, default=1.0, help='scoring weight for MFE (default: 1.0)')
    grp.add_argument('--folding-start-structure-width', type=int, default=15, help='width in nt of unfolded region near the start codon (default: 15)')
    grp.add_argument('--folding-start-structure-weight', type=int, default=1, help='penalty weight for folded start codon region (default: 1)')

    grp = parser.add_argument_group('Fitness - Tandem Repeats')
    grp.add_argument('--repeats-min-repeats', type=int, default=2, help='minimum number of repeats to be considered as a tandem repeat (default: 2)')
    grp.add_argument('--repeats-repeat-length', type=int, default=10, help='minimum length of repeats to be considered as a tandem repeat (default: 10)')
    grp.add_argument('--repeats-weight', type=float, default=1.0, help='scoring weight for tandem repeats (default: 1.0)')

    parser.add_argument('fasta', help='input fasta file containing the CDS sequence')

    return parser.parse_args()

def run_vaxpress():
    args = parse_options()

    inputseq = next(SeqIO.parse(args.fasta, 'fasta'))
    seqdescr = inputseq.description
    cdsseq = str(inputseq.seq).replace('T', 'U')
    if len(cdsseq) % 3 != 0:
        raise ValueError('Invalid CDS sequence length')

    invalid_letters = set(cdsseq) - set('ACGU')
    if invalid_letters:
        raise ValueError(f'Invalid letters in CDS sequence: {",".join(invalid_letters)}')

    scoring_options = ScoringOptions(
        iCodon_species=args.icodon_species,
        iCodon_weight=args.icodon_weight,
        ucount_weight=args.ucount_weight,
        gc_window_size=args.gc_window_size,
        gc_stride=args.gc_stride,
        gc_weight=args.gc_weight,
        folding_off=args.folding_off,
        folding_engine=args.folding_engine,
        folding_mfe_weight=args.folding_mfe_weight,
        folding_start_structure_width=args.folding_start_structure_width,
        folding_start_structure_weight=args.folding_start_structure_weight,
        repeats_min_repeats=args.repeats_min_repeats,
        repeats_repeat_length=args.repeats_repeat_length,
        repeats_weight=args.repeats_weight,
    )

    iteration_options = IterationOptions(
        n_iterations=args.iterations,
        n_offsprings=args.offsprings,
        n_survivors=args.survivors,
        initial_mutation_rate=args.initial_mutation_rate,
        winddown_trigger=args.winddown_trigger,
        winddown_rate=args.winddown_rate,
    )

    evochamber = CDSEvolutionChamber(
        cdsseq, args.output, scoring_options, iteration_options,
        seed=args.seed, processes=args.processes,
        codon_table=args.codon_table, quiet=args.quiet, seq_description=seqdescr,
        print_top_mutants=args.print_top, random_initialization=args.random_initialization)

    evochamber.run()


if __name__ == '__main__':
    run_vaxpress()
