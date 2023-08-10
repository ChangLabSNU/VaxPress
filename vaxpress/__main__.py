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

from . import scoring
from .evolution_chamber import (
    CDSEvolutionChamber, IterationOptions, ExecutionOptions)
from Bio import SeqIO
import argparse

SPECIES_ALIASES = {
    'human': 'Homo sapiens',
    'mouse': 'Mus musculus',
    'zebrafish': 'Danio rerio',
    'rat': 'Rattus norvegicus',
    'macaque': 'Macaca mulatta',
}

def parse_options(scoring_funcs):
    parser = argparse.ArgumentParser(
        prog='vaxpress',
        description='VaxPress: A Codon Optimizer for mRNA Vaccine Design')

    grp = parser.add_argument_group('Input/Output Options')
    grp.add_argument('-i', '--input', required=True, help='input fasta file containing the CDS sequence')
    grp.add_argument('--protein', default=False, action='store_true', help='input is a protein sequence')
    grp.add_argument('-o', '--output', required=True, help='output file')
    grp.add_argument('-q', '--quiet', default=False, action='store_true', help='do not print progress')
    grp.add_argument('--print-top', type=int, default=10, help='print top and bottom N sequences (default: 10)')

    grp = parser.add_argument_group('Execution Options')
    grp.add_argument('-p', '--processes', type=int, default=4, help='number of processes to use (default: 4)')
    grp.add_argument('--seed', type=int, default=922, help='random seed (default: 922)')
    grp.add_argument('--species', default='human', help='target species (default: human)')
    grp.add_argument('--codon-table', default='standard', help='codon table (default: standard)')
    grp.add_argument('--random-initialization', default=False, action='store_true', help='randomize all codons at the beginning')

    grp = parser.add_argument_group('Optimization Options')
    grp.add_argument('--iterations', type=int, default=10, help='number of iterations (default: 10)')
    grp.add_argument('--offsprings', type=int, default=20, help='number of offsprings per iteration (default: 20)')
    grp.add_argument('--survivors', type=int, default=2, help='number of survivors per iteration (default: 2)')
    grp.add_argument('--initial-mutation-rate', type=float, default=0.1, help='initial mutation rate (default: 0.1)')
    grp.add_argument('--winddown-trigger', type=int, default=15, help='number of iterations with the same best score to trigger mutation stabilization (default: 15)')
    grp.add_argument('--winddown-rate', type=float, default=0.9, help='mutation rate multiplier when mutation stabilization is triggered (default: 0.9)')

    argmaps = []
    for func in sorted(scoring_funcs.values(), key=lambda f: f.priority):
        argmap = func.add_argument_parser(parser)
        argmaps.append((func, argmap))

    args = parser.parse_args()
    scoring_opts = {}
    for func, argmap in argmaps:
        opts = scoring_opts[func.name] = {}
        for optname, varname in argmap:
            opts[varname] = getattr(args, optname[2:].replace('-', '_'))

    return args, scoring_opts

def run_vaxpress():
    scoring_funcs = scoring.discover_scoring_functions()

    args, scoring_options = parse_options(scoring_funcs)

    inputseq = next(SeqIO.parse(args.input, 'fasta'))
    seqdescr = inputseq.description
    cdsseq = str(inputseq.seq)

    iteration_options = IterationOptions(
        n_iterations=args.iterations,
        n_offsprings=args.offsprings,
        n_survivors=args.survivors,
        initial_mutation_rate=args.initial_mutation_rate,
        winddown_trigger=args.winddown_trigger,
        winddown_rate=args.winddown_rate,
    )

    execution_options = ExecutionOptions(
        seed=args.seed,
        processes=args.processes,
        random_initialization=args.random_initialization,
        species=SPECIES_ALIASES.get(args.species, args.species),
        codon_table=args.codon_table,
        quiet=args.quiet,
        seq_description=seqdescr,
        print_top_mutants=args.print_top,
        protein=args.protein,
    )

    evochamber = CDSEvolutionChamber(
        cdsseq, args.output, scoring_funcs, scoring_options,
        iteration_options, execution_options)

    return evochamber.run()


if __name__ == '__main__':
    import sys
    ret = run_vaxpress()
    sys.exit(ret)
