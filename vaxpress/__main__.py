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

from . import scoring, config, __version__
from .evolution_chamber import (
    CDSEvolutionChamber, IterationOptions, ExecutionOptions)
from .presets import load_preset
from .reporting import ReportGenerator
from Bio import SeqIO
import argparse
import shlex
import time
import sys
import os

SPECIES_ALIASES = {
    'human': 'Homo sapiens',
    'mouse': 'Mus musculus',
    'zebrafish': 'Danio rerio',
    'rat': 'Rattus norvegicus',
    'macaque': 'Macaca mulatta',
}

CONSERVATIVE_START_DEFAULT_WIDTH = 7
BOOST_LOOP_MUTATIONS_DEFAULT_WIDTH = 15

def preparse_config_preset_addons():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--preset', type=str, required=False, default=None)
    parser.add_argument('--addon', type=str, action='append')
    args, _ = parser.parse_known_args()

    preset = config.load_config()

    if args.preset is not None:
        try:
            preset.update(load_preset(open(args.preset).read()))
        except Exception:
            print(f'Failed to load the preset from {args.preset}.')
            sys.exit(1)

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

    ignore_options = ['addons', 'command_line']

    for argname, argval in preset.items():
        if argname in ignore_options:
            continue
        elif argname != 'fitness':
            optname = '--' + argname.replace('_', '-')
            fix_option(optmap[optname], argval)
            continue

        for grpname, grpvalues in argval.items():
            for optname, optval in grpvalues.items():
                optname = f'--{grpname}-{optname}'.replace('_', '-')
                fix_option(optmap[optname], optval)

def check_lineardesign(args):
    if args.lineardesign is None:
        return

    if args.lineardesign_dir is None:
        print('Specify the path to the LinearDesign top directory with '
              '--lineardesign-dir.', file=sys.stderr)
        sys.exit(1)

    executable = os.path.join(args.lineardesign_dir, 'bin', 'LinearDesign_2D')
    if not os.path.exists(executable):
        print('LinearDesign is not available. Please specify the correct path '
              'to the LinearDesign top directory with --lineardesign-dir.',
              file=sys.stderr)
        sys.exit(1)

def check_argument_validity(args):
    check_lineardesign(args)

    if args.conservative_start is not None:
        try:
            if args.conservative_start.count(':') == 1:
                cons_iter, cons_width = args.conservative_start.split(':', 1)
                cons_iter, cons_width = int(cons_iter), int(cons_width)
            elif ':' in args.conservative_start:
                raise ValueError
            else:
                cons_iter = int(args.conservative_start)
                cons_width = CONSERVATIVE_START_DEFAULT_WIDTH

            if not (1 <= cons_iter <= args.iterations):
                print('Invalid value for --conservative-start. ITER must be '
                      'between 1 and the maximum iteration number.',
                      file=sys.stderr)
                sys.exit(1)
            if cons_width <= 0:
                print('Invalid value for --conservative-start. WIDTH must be '
                      'a positive integer.', file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print('Invalid format for --conservative-start. Use '
                'ITER[:WIDTH] format.', file=sys.stderr)
            sys.exit(1)
        else:
            args.conservative_start = f'{cons_iter}:{cons_width}'

    if args.boost_loop_mutations is not None:
        try:
            if args.boost_loop_mutations.count(':') == 1:
                boost_weight, boost_start = args.boost_loop_mutations.split(':', 1)
                boost_weight, boost_start = float(boost_weight), int(boost_start)
            elif ':' in args.boost_loop_mutations:
                raise ValueError
            else:
                boost_weight = float(args.boost_loop_mutations)
                boost_start = BOOST_LOOP_MUTATIONS_DEFAULT_WIDTH

            if boost_weight < 0:
                print('Invalid value for --boost-loop-mutations. WEIGHT must be '
                      'a non-negative number.', file=sys.stderr)
                sys.exit(1)
            if boost_start < 0:
                print('Invalid value for --boost-loop-mutations. START must be '
                      'a non-negative integer.', file=sys.stderr)
                sys.exit(1)
        except ValueError:
            print('Invalid format for --boost-loop-mutations. Use '
                'WEIGHT[:START] format.', file=sys.stderr)
            sys.exit(1)
        else:
            args.boost_loop_mutations = f'{boost_weight}:{boost_start}'

def parse_options(scoring_funcs, preset):
    parser = argparse.ArgumentParser(
        prog='vaxpress',
        description='VaxPress: A Codon Optimizer for mRNA Vaccine Design')

    grp = parser.add_argument_group('Input/Output Options')
    grp.add_argument('-i', '--input', required=True, metavar='FILE',
                     help='input fasta file containing the CDS sequence')
    grp.add_argument('--protein', default=False, action='store_true',
                     help='input is a protein sequence')
    grp.add_argument('-o', '--output', required=True, metavar='DIR',
                     help='output directory')
    grp.add_argument('--overwrite', action='store_true',
                     help='overwrite output directory if it already exists')
    grp.add_argument('-q', '--quiet', default=False, action='store_true',
                     help='do not print progress')
    grp.add_argument('--print-top', type=int, default=10, metavar='N',
                     help='print top and bottom N sequences (default: 10)')
    grp.add_argument('--report-interval', type=int, default=5, metavar='MIN',
                     help='report interval in minutes (default: 5)')
    grp.add_argument('--version', action='version', version=__version__)

    grp = parser.add_argument_group('Execution Options')
    grp.add_argument('--preset', type=str, required=False, default=None,
                     metavar='FILE', help='use preset values in parameters.json')
    grp.add_argument('--addon', type=str, action='append', metavar='FILE',
                     help='load a third-party fitness function')
    grp.add_argument('-p', '--processes', type=int, default=4, metavar='N',
                     help='number of processes to use (default: 4)')
    grp.add_argument('--seed', type=int, default=922, metavar='NUMBER',
                     help='random seed (default: 922)')
    grp.add_argument('--folding-engine', default='vienna', metavar='NAME',
                     choices=['vienna', 'linearfold'],
                     help='RNA folding engine: vienna or linearfold '
                          '(default: vienna)')

    grp = parser.add_argument_group('Optimization Options')
    grp.add_argument('--random-initialization', action='store_true',
                     default=False, help='randomize all codons at the beginning')
    grp.add_argument('--conservative-start', default=None, metavar='ITER[:WIDTH]',
                     help='conserve sequence for the first ITER iterations '
                          'except the first WIDTH amino acids')
    grp.add_argument('--iterations', type=int, default=10, metavar='N',
                     help='number of iterations (default: 10)')
    grp.add_argument('--offsprings', type=int, default=20, metavar='N',
                     help='number of offsprings per iteration (default: 20)')
    grp.add_argument('--survivors', type=int, default=2, metavar='N',
                     help='number of survivors per iteration (default: 2)')
    grp.add_argument('--initial-mutation-rate', type=float, default=0.1,
                     metavar='RATE',
                     help='initial mutation rate (default: 0.1)')
    grp.add_argument('--boost-loop-mutations',
                     default=f'3:{BOOST_LOOP_MUTATIONS_DEFAULT_WIDTH}',
                     metavar='WEIGHT[:START]', type=str,
                     help='boost mutations in loops after position START '
                          'by WEIGHT (default: 3:'
                          f'{BOOST_LOOP_MUTATIONS_DEFAULT_WIDTH})')
    grp.add_argument('--winddown-trigger', type=int, default=15, metavar='N',
                     help='number of iterations with the same best score to '
                          'trigger mutation stabilization (default: 15)')
    grp.add_argument('--winddown-rate', type=float, default=0.9, metavar='RATE',
                     help='mutation rate multiplier when mutation stabilization '
                          'is triggered (default: 0.9)')
    grp.add_argument('--species', default='human', metavar='NAME',
                     help='target species (default: human)')
    grp.add_argument('--codon-table', default='standard', metavar='NAME',
                     help='codon table (default: standard)')

    grp = parser.add_argument_group('LinearDesign Options')
    grp.add_argument('--lineardesign', type=float, default=None,
                     metavar='LAMBDA',
                     help='call LinearDesign to initialize the optimization')
    grp.add_argument('--lineardesign-dir', type=str, default=None, metavar='DIR',
                     help='path to the top directory containing LinearDesign')
    grp.add_argument('--lineardesign-omit-start', type=int, metavar='AA', default=5,
                     help='number of amino acids to omit from the N-terminus '
                          'when calling LinearDesign (default: 5)')

    argmaps = []
    for func in sorted(scoring_funcs.values(), key=lambda f: f.priority):
        argmap = func.add_argument_parser(parser)
        argmaps.append((func, argmap))

    if preset:
        apply_preset(parser, preset)

    args = parser.parse_args()
    scoring_opts = {}
    for func, argmap in argmaps:
        opts = scoring_opts[func.name] = {}
        for optname, varname in argmap:
            opts[varname] = getattr(args, optname[2:].replace('-', '_'))

    config.initialize_config_if_needed(args)
    check_argument_validity(args)

    return args, scoring_opts

def run_vaxpress():
    preset, addon_paths = preparse_config_preset_addons()
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
        conservative_start=args.conservative_start,
        boost_loop_mutations=args.boost_loop_mutations,
        species=SPECIES_ALIASES.get(args.species, args.species),
        codon_table=args.codon_table,
        quiet=args.quiet,
        seq_description=seqdescr,
        print_top_mutants=args.print_top,
        protein=args.protein,
        addons=addon_paths,
        lineardesign_dir=args.lineardesign_dir,
        lineardesign_lambda=args.lineardesign,
        lineardesign_omit_start=args.lineardesign_omit_start,
        folding_engine=args.folding_engine,
    )

    next_report = 0 # Generate the first report immediately.
    # vaxpress assumes that the system clock does not go back or jump forward.

    try:
        evochamber = CDSEvolutionChamber(
            cdsseq, scoring_funcs, scoring_options,
            iteration_options, execution_options)

        status = None
        for status in evochamber.run():
            do_report = len(status['time']) > 1 and (
                (status['iter_no'] < 0) or (status['time'][-1] >= next_report))

            if do_report:
                next_report = status['time'][-1] + args.report_interval * 60
                if status['iter_no'] >= 0:
                    evochamber.printmsg('==> Generating intermediate report...')

                evaldata = evochamber.save_results()
                status.update({'evaluations': evaldata, 'version': __version__})

                generate_report(status, args, scoring_options, iteration_options,
                                execution_options, inputseq, scoring_funcs)

        finished = (status is not None and status['iter_no'] < 0
                    and status['error'] == 0)
        if finished:
            evochamber.printmsg(
                'Finished successfully. You can view the results '
                f'in {evochamber.outputdir.rstrip("/")}/report.html.')

        return status['error'] if status is not None else 1
    except KeyboardInterrupt:
        return 1
    except FileExistsError:
        print('Output directory already exists. Use --overwrite '
              'option to overwrite it.')
        return 1

def generate_report(status, args, scoring_options, iteration_options,
                    execution_options, inputseq, scoring_funcs):
    if status['iter_no'] > 0: # Intermediate report
        total_elapsed = status['time'][-1] - status['time'][0]
        time_per_iteration = total_elapsed / status['iter_no']
        remaining = (iteration_options.n_iterations -
                     status['iter_no']) * time_per_iteration

        expected_end = time.time() + remaining

        status['speed'] = time_per_iteration
        status['expected_end'] = expected_end
        status['progress_percentage'] = int(100 * status['iter_no'] /
                                            iteration_options.n_iterations)
        status['refresh'] = args.report_interval * 60 + 5 # 5 seconds for safety

    ReportGenerator(status, args, scoring_options, iteration_options,
                    execution_options, inputseq, scoring_funcs).generate()

if __name__ == '__main__':
    ret = run_vaxpress()
    sys.exit(ret)
