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
import click

@click.command()
@click.option('-o', '--output', required=True, help='output file')
@click.option('--seed', type=int, default=922, help='random seed')
@click.option('--processes', default=5, help='number of processes to use')
@click.option('--quiet', is_flag=True, help='do not print progress')
@click.option('--print-top', default=10, help='print top and bottom N sequences')
@click.option('--codon-table', default='standard', help='codon table')
@click.option('--random-initialization', is_flag=True, help='randomize all codons at the beginning')
# Iteration parameters
@click.option('--iterations', default=10, help='number of iterations')
@click.option('--offsprings', default=4, help='number of offsprings per iteration')
@click.option('--survivors', default=2, help='number of survivors per iteration')
@click.option('--initial-mutation-rate', default=0.1, help='initial mutation rate')
@click.option('--winddown-trigger', default=15, help='number of iterations with the same best score to trigger mutation stabilization')
@click.option('--winddown-rate', default=0.9, help='mutation rate multiplier when mutation stabilization is triggered')
# iCodon parameters
@click.option('--icodon-species', default='human', help='iCodon RNA stability optimizer: species')
@click.option('--icodon-weight', default=1.0, help='scoring weight for iCodon predicted stability')
# U count parameters
@click.option('--ucount-weight', default=3.0, help='scoring weight for U count minimizer')
# GC ratio parameters
@click.option('--gc-window-size', default=50, help='size of window for GC content calculation')
@click.option('--gc-stride', default=5, help='size of stride for GC content calculation')
@click.option('--gc-weight', default=3, help='GC penalty score')
# Secondary structure parameters
@click.option('--folding-off', is_flag=True, help='disable secondary structure folding')
@click.option('--folding-engine', default='vienna', help='RNA folding engine')
@click.option('--folding-mfe-weight', default=1.0, help='scoring weight for MFE')
@click.option('--folding-start-structure-width', default=15, help='width in nt of unfolded region near the start codon')
@click.option('--folding-start-structure-weight', default=1, help='penalty weight for folded start codon')
# Tandem repeats parameters
@click.option('--repeats-min-repeats', default=2, help='minimum number of repeats')
@click.option('--repeats-repeat-length', default=10, help='minimum length of repeats')
@click.option('--repeats-weight', default=1.0, help='scoring weight for tandem repeats')
# Arguments
@click.argument('fasta', required=True)
def run_vaxpress(output, seed, processes, quiet, print_top, codon_table, random_initialization,
                 iterations, offsprings, survivors, initial_mutation_rate, winddown_trigger,
                 winddown_rate, icodon_species, icodon_weight, ucount_weight,
                 gc_window_size, gc_stride, gc_weight,
                 folding_off, folding_engine, folding_mfe_weight,
                 folding_start_structure_width, folding_start_structure_weight,
                 repeats_min_repeats, repeats_repeat_length, repeats_weight,
                 fasta):

    inputseq = next(SeqIO.parse(fasta, 'fasta'))
    seqdescr = inputseq.description
    cdsseq = str(inputseq.seq).replace('T', 'U')
    if len(cdsseq) % 3 != 0:
        raise ValueError('Invalid CDS sequence length')

    invalid_letters = set(cdsseq) - set('ACGU')
    if invalid_letters:
        raise ValueError(f'Invalid letters in CDS sequence: {",".join(invalid_letters)}')

    scoring_options = ScoringOptions(
        iCodon_species=icodon_species,
        iCodon_weight=icodon_weight,
        ucount_weight=ucount_weight,
        gc_window_size=gc_window_size,
        gc_stride=gc_stride,
        gc_weight=gc_weight,
        folding_off=folding_off,
        folding_engine=folding_engine,
        folding_mfe_weight=folding_mfe_weight,
        folding_start_structure_width=folding_start_structure_width,
        folding_start_structure_weight=folding_start_structure_weight,
        repeats_min_repeats=repeats_min_repeats,
        repeats_repeat_length=repeats_repeat_length,
        repeats_weight=repeats_weight,
    )

    iteration_options = IterationOptions(
        n_iterations=iterations,
        n_offsprings=offsprings,
        n_survivors=survivors,
        initial_mutation_rate=initial_mutation_rate,
        winddown_trigger=winddown_trigger,
        winddown_rate=winddown_rate,
    )

    evochamber = CDSEvolutionChamber(
        cdsseq, output, scoring_options, iteration_options,
        seed=seed, processes=processes,
        codon_table=codon_table, quiet=quiet, seq_description=seqdescr,
        print_top_mutants=print_top, random_initialization=random_initialization)

    evochamber.run()


if __name__ == '__main__':
    run_vaxpress()
