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
from .presets import load_preset
from .reporting import ReportGenerator
from Bio import SeqIO
import argparse
import shlex
import os

SPECIES_ALIASES = {
    'human': 'Homo sapiens',
    'mouse': 'Mus musculus',
    'zebrafish': 'Danio rerio',
    'rat': 'Rattus norvegicus',
    'macaque': 'Macaca mulatta',
}

def preparse_preset_and_addons():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--preset', type=str, required=False, default=None)
    parser.add_argument('--addon', type=str, action='append')
    args, _ = parser.parse_known_args()

    if args.preset is not None:
        try:
            preset = load_preset(open(args.preset).read())
        except Exception:
            print(f'Failed to load the preset from {args.preset}.')
            sys.exit(1)
    else:
        preset = None

    addon_paths = []
    if preset is not None and 'addons' in preset:
        addon_paths.extend(preset['addons'])

    if args.addon is not None:
        for path in args.addon:
            if os.path.exists(path):
                addon_paths.append(path)
            else:
                print(f'Addon path {path} is missing.')
                sys.exit(1)

    return preset, addon_paths

def apply_preset(main_parser, preset):
    optmap = main_parser._option_string_actions

    def fix_option(opt, newval):
        if opt.default == newval:
            return

        opt.default = newval

        # Fix store_action for boolean options
        if isinstance(newval, bool):
            opt.const = not newval

        # Fix default value in help string
        if '(default:' in opt.help:
            prefix = opt.help.split('(default:')[0]
            opt.help = f'{prefix}(default: {newval})'

    for argname, argval in preset.items():
        if argname == 'addons':
            continue
        elif argname != 'fitness':
            optname = '--' + argname.replace('_', '-')
            fix_option(optmap[optname], argval)
            continue

        for grpname, grpvalues in argval.items():
            for optname, optval in grpvalues.items():
                optname = f'--{grpname}-{optname}'.replace('_', '-')
                fix_option(optmap[optname], optval)

def parse_options(scoring_funcs, preset):
    parser = argparse.ArgumentParser(
        prog='vaxpress',
        description='VaxPress: A Codon Optimizer for mRNA Vaccine Design')

    grp = parser.add_argument_group('Input/Output Options')
    grp.add_argument('-i', '--input', required=True, help='input fasta file containing the CDS sequence')
    grp.add_argument('--protein', default=False, action='store_true', help='input is a protein sequence')
    grp.add_argument('-o', '--output', required=True, help='output directory')
    grp.add_argument('--overwrite', action='store_true', help='overwrite output directory if it already exists')
    grp.add_argument('-q', '--quiet', default=False, action='store_true', help='do not print progress')
    grp.add_argument('--print-top', type=int, default=10, help='print top and bottom N sequences (default: 10)')

    grp = parser.add_argument_group('Execution Options')
    grp.add_argument('--preset', type=str, required=False, default=None, help='use preset values in parameters.json')
    grp.add_argument('--addon', type=str, action='append', help='load a third-party fitness function')
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

    if preset is not None:
        apply_preset(parser, preset)

    args = parser.parse_args()
    scoring_opts = {}
    for func, argmap in argmaps:
        opts = scoring_opts[func.name] = {}
        for optname, varname in argmap:
            opts[varname] = getattr(args, optname[2:].replace('-', '_'))

    return args, scoring_opts

def run_vaxpress():
    preset, addon_paths = preparse_preset_and_addons()
    scoring_funcs = scoring.discover_scoring_functions(addon_paths)

    args, scoring_options = parse_options(scoring_funcs, preset)

    inputseq = next(SeqIO.parse(args.input, 'fasta'))
    seqdescr = inputseq.description
    cdsseq = str(inputseq.seq)

    command_line = ' '.join(shlex.quote(arg) for arg in sys.argv)

    iteration_options = IterationOptions(
        n_iterations=args.iterations,
        n_offsprings=args.offsprings,
        n_survivors=args.survivors,
        initial_mutation_rate=args.initial_mutation_rate,
        winddown_trigger=args.winddown_trigger,
        winddown_rate=args.winddown_rate,
    )

    execution_options = ExecutionOptions(
        output=args.output,
        command_line=command_line,
        overwrite=args.overwrite,
        seed=args.seed,
        processes=args.processes,
        random_initialization=args.random_initialization,
        species=SPECIES_ALIASES.get(args.species, args.species),
        codon_table=args.codon_table,
        quiet=args.quiet,
        seq_description=seqdescr,
        print_top_mutants=args.print_top,
        protein=args.protein,
        addons=addon_paths,
    )

    try:
        evochamber = CDSEvolutionChamber(
            cdsseq, scoring_funcs, scoring_options,
            iteration_options, execution_options)

        result = evochamber.run()
        generate_report(result, args, scoring_options, iteration_options,
                        execution_options, inputseq)
        return result['error']
    except KeyboardInterrupt:
        return 1
    except FileExistsError:
        print('Output directory already exists. Use --overwrite '
              'option to overwrite it.')
        return 1

def generate_report(result, args, scoring_options, iteration_options,
                    execution_options, inputseq):
    # Save arguments and parameters for debugging and inspection.
    # May be removed in the future.
    import pickle
    pickle.dump({'args': args, 'scoring_options': scoring_options,
                'iteration_options': iteration_options,
                'execution_options': execution_options,
                'seq': inputseq, 'result': result},
                open(execution_options.output + '/report_data.pickle', 'wb'))

    ReportGenerator(result, args, scoring_options, iteration_options,
                    execution_options, inputseq).generate()

if __name__ == '__main__':
    import sys
    ret = run_vaxpress()
    sys.exit(ret)
