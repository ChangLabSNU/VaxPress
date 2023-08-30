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

import numpy as np
import time
import sys
import os
import shutil
from textwrap import wrap
from tabulate import tabulate
from collections import namedtuple
from concurrent import futures
from itertools import cycle
from .mutant_generator import MutantGenerator, STOP
from .sequence_evaluator import SequenceEvaluator
from .presets import dump_to_preset
from .console import hbar, hbar_double
from . import __version__

PROTEIN_ALPHABETS = 'ACDEFGHIKLMNPQRSTVWY' + STOP
RNA_ALPHABETS = 'ACGU'

IterationOptions = namedtuple('IterationOptions', [
    'n_iterations', 'n_offsprings', 'n_survivors', 'initial_mutation_rate',
    'winddown_trigger', 'winddown_rate'
])

ExecutionOptions = namedtuple('ExecutionOptions', [
    'output', 'command_line', 'overwrite', 'seed', 'processes',
    'random_initialization', 'conservative_start', 'boost_loop_mutations',
    'species', 'codon_table', 'protein', 'quiet',
    'seq_description', 'print_top_mutants', 'addons',
    'lineardesign_dir', 'lineardesign_lambda', 'lineardesign_omit_start',
    'folding_engine',
])

class CDSEvolutionChamber:

    stop_threshold = 0.2
    table_header_length = 6

    finalized_seqs = None
    checkpoint_path = None
    fasta_line_width = 72

    def __init__(self, cdsseq: str, scoring_funcs: dict,
                 scoring_options: dict, iteration_options: IterationOptions,
                 exec_options: ExecutionOptions):
        self.cdsseq = cdsseq.upper()

        self.seq_description = exec_options.seq_description
        self.outputdir = exec_options.output
        self.scoringfuncs = scoring_funcs
        self.scoreopts = scoring_options
        self.iteropts = iteration_options
        self.execopts = exec_options
        self.n_processes = exec_options.processes
        self.quiet = exec_options.quiet
        self.print_top_mutants = exec_options.print_top_mutants

        self.initialize()

    def printmsg(self, *args, **kwargs) -> None:
        if not self.quiet or kwargs.get('force') is not None:
            if 'force' in kwargs:
                del kwargs['force']
            kwargs['file'] = sys.stderr
            print(*args, **kwargs)

        if 'force' in kwargs:
            del kwargs['force']
        kwargs['file'] = self.log_file
        print(*args, **kwargs)

    def initialize(self) -> None:
        if os.path.exists(self.outputdir):
            if self.execopts.overwrite:
                if os.path.isdir(self.outputdir):
                    shutil.rmtree(self.outputdir)
                else:
                    os.unlink(self.outputdir)
            else:
                raise FileExistsError('Output directory already exists.')

        os.makedirs(self.outputdir)
        self.checkpoint_path = os.path.join(self.outputdir, 'checkpoints.tsv')
        self.log_file = open(os.path.join(self.outputdir, 'log.txt'), 'w')

        if self.execopts.protein:
            invalid_letters = set(self.cdsseq) - set(PROTEIN_ALPHABETS)
            if invalid_letters:
                raise ValueError('Invalid protein sequence: '
                                 f'{" ".join(invalid_letters)}')
            if self.cdsseq[-1] != STOP:
                self.cdsseq += STOP
        else: # RNA or DNA
            self.cdsseq = self.cdsseq.replace('T', 'U')
            invalid_letters = set(self.cdsseq) - set(RNA_ALPHABETS)
            if invalid_letters:
                raise ValueError(f'Invalid RNA sequence: {" ".join(invalid_letters)}')
            if len(self.cdsseq) % 3 != 0:
                raise ValueError('Invalid CDS sequence length')

        self.species = self.execopts.species
        self.rand = np.random.RandomState(self.execopts.seed)
        self.mutantgen = MutantGenerator(self.cdsseq, self.rand,
                                         self.execopts.codon_table,
                                         self.execopts.protein,
                                         self.execopts.boost_loop_mutations)
        if self.execopts.lineardesign_lambda is not None:
            self.printmsg('==> Initializing sequence with LinearDesign...')

            self.mutantgen.lineardesign_initial_codons(
                self.execopts.lineardesign_lambda,
                self.execopts.lineardesign_dir,
                self.execopts.lineardesign_omit_start)
        elif self.execopts.random_initialization or self.execopts.protein:
            self.mutantgen.randomize_initial_codons()
        self.population = [self.mutantgen.initial_codons]
        self.population_foldings = [None]

        self.mutation_rate = self.iteropts.initial_mutation_rate

        self.length_aa = len(self.population[0])
        self.length_cds = len(self.cdsseq)

        if self.execopts.conservative_start is not None:
            cstart_iter, cstart_width = self.execopts.conservative_start.split(':')
            self.alternative_mutation_fields = [
                (0, int(cstart_iter),
                 self.mutantgen.prepare_alternative_choices(0, int(cstart_width)))]
        else:
            self.alternative_mutation_fields = []

        self.seqeval = SequenceEvaluator(self.scoringfuncs, self.scoreopts,
                                    self.execopts, self.mutantgen, self.species,
                                    self.length_cds, self.quiet, self.printmsg)
        self.penalty_metric_flags = self.seqeval.penalty_metric_flags # XXX

        self.initial_sequence_evaluation = (
            self.seqeval.prepare_evaluation_data(''.join(self.population[0])))

        self.best_scores = []
        self.elapsed_times = []
        self.checkpoint_file = open(self.checkpoint_path, 'w')
        self.checkpoint_header_written = False

    def show_configuration(self) -> None:
        spec = self.mutantgen.compute_mutational_space()

        self.printmsg(f'VaxPress Codon Optimizer for mRNA Vaccines {__version__}')
        self.printmsg(hbar_double)
        self.printmsg(f' * Name: {self.seq_description}')
        self.printmsg(f' * CDS length: {self.length_cds} nt')
        self.printmsg(f' * Possible single mutations: {spec["singles"]}')
        self.printmsg(f' * Possible sequences: {spec["total"]}')
        self.printmsg(f' * Command line: {" ".join(sys.argv)}')
        self.printmsg()

    def mutate_population(self, iter_no0: int) -> None:
        nextgeneration = self.population[:]

        choices = None
        for begin, end, altchoices in self.alternative_mutation_fields:
            if begin <= iter_no0 < end:
                choices = altchoices
                break

        assert len(self.population) == len(self.population_foldings)

        n_new_mutants = max(0, self.iteropts.n_offsprings - len(self.population))
        for parent, parent_folding, _ in zip(cycle(self.population),
                                             cycle(self.population_foldings),
                                             range(n_new_mutants)):
            child = self.mutantgen.generate_mutant(parent, self.mutation_rate,
                                                   choices, parent_folding)
            nextgeneration.append(child)

        self.population[:] = nextgeneration
        self.flatten_seqs = [''.join(p) for p in self.population]

    def run(self) -> dict:
        if not self.quiet:
            self.show_configuration()

        timelogs = [time.time()]
        n_survivors = self.iteropts.n_survivors
        last_winddown = 0
        error_code = 0

        with futures.ProcessPoolExecutor(max_workers=self.n_processes) as executor:

            if self.iteropts.n_iterations == 0:
                # Only the initial sequence is evaluated
                self.flatten_seqs = [''.join(self.population[0])]
                total_scores, scores, metrics, foldings = self.seqeval.evaluate(
                                                    self.flatten_seqs, executor)
                if total_scores is None:
                    error_code = 1
                else:
                    self.write_checkpoint(0, [0], total_scores, scores, metrics,
                                          foldings)
                    timelogs.append(time.time())

            for i in range(self.iteropts.n_iterations):
                iter_no = i + 1
                n_parents = len(self.population)

                self.expected_total_mutations = (
                    self.mutantgen.compute_expected_mutations(self.mutation_rate))
                if self.expected_total_mutations < self.stop_threshold:
                    self.printmsg('==> Stopping: expected mutation reaches the minimum')
                    break

                self.printmsg(hbar)
                self.printmsg(f'Iteration {iter_no}/{self.iteropts.n_iterations}  --',
                              f'  mut_rate: {self.mutation_rate:.5f} --',
                              f'E(muts): {self.expected_total_mutations:.1f}')

                self.mutate_population(i)
                total_scores, scores, metrics, foldings = self.seqeval.evaluate(
                                                    self.flatten_seqs, executor)
                if total_scores is None:
                    # Termination due to errors from one or more scoring functions
                    error_code = 1
                    break

                ind_sorted = np.argsort(total_scores)[::-1]
                survivor_indices = ind_sorted[:n_survivors]
                survivors = [self.population[i] for i in survivor_indices]
                survivor_foldings = [foldings[i] for i in survivor_indices]
                self.best_scores.append(total_scores[ind_sorted[0]])

                # Write the evaluation result of the initial sequence in
                # the first iteration
                if i == 0:
                    self.write_checkpoint(0, [0], total_scores, scores,
                                          metrics, foldings)

                self.print_eval_results(total_scores, metrics, ind_sorted, n_parents)
                self.write_checkpoint(iter_no, survivor_indices, total_scores,
                                      scores, metrics, foldings)

                self.population[:] = survivors
                self.population_foldings[:] = survivor_foldings

                self.printmsg(' # Last best scores:',
                              ' '.join(f'{s:.3f}' for s in self.best_scores[-5:]))
                if (len(self.best_scores) >= self.iteropts.winddown_trigger and
                        iter_no - last_winddown > self.iteropts.winddown_trigger):
                    if (self.best_scores[-1] <=
                            self.best_scores[-self.iteropts.winddown_trigger]):
                        self.mutation_rate *= self.iteropts.winddown_rate
                        self.printmsg('==> Winddown triggered: mutation rate '
                                      f'= {self.mutation_rate:.5f}')
                        last_winddown = iter_no

                timelogs.append(time.time())

                self.print_time_estimation(timelogs[-2], timelogs[-1], iter_no)

                self.printmsg()

                yield {'iter_no': iter_no, 'error': error_code, 'time': timelogs}

        yield {'iter_no': -1, 'error': error_code, 'time': timelogs}

    def print_eval_results(self, total_scores, metrics, ind_sorted, n_parents) -> None:
        if self.quiet:
            return

        print_top = min(self.print_top_mutants, len(self.population))
        rowstoshow = ind_sorted[:print_top]
        if len(rowstoshow) < 1:
            return

        metrics_to_show = sorted(k for k in metrics[rowstoshow[0]].keys()
                                 if k not in self.penalty_metric_flags)
        header = ['flags', 'score'] + metrics_to_show
        tabdata = []
        for rank, i in enumerate(rowstoshow):
            flags = [
                'P' if i < n_parents else '-', # is parent
                'S ' if rank < self.iteropts.n_survivors else '- '] # is survivor
            for name, flag in self.penalty_metric_flags.items():
                flags.append(flag if metrics[i][name] != 0 in metrics[i] else '-')
            
            f_total = total_scores[i]
            f_metrics = [metrics[i][name] for name in header[2:]]
            tabdata.append([''.join(flags), f_total] +f_metrics)

        header_short = [h[:self.table_header_length] for h in header]
        self.printmsg(tabulate(tabdata, header_short, tablefmt='simple',
                               floatfmt='.2f'), end='\n\n')

    def print_time_estimation(self, iteration_start: float, iteration_end: float,
                              iter_no: int) -> None:
        elapsed = iteration_end - iteration_start
        self.elapsed_times.append(elapsed)

        mean_elapsed = np.mean(self.elapsed_times[-5:])
        remaining = (self.iteropts.n_iterations - iter_no) * mean_elapsed

        expected_end = time.asctime(time.localtime(time.time() + remaining))
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        if elapsed_str.startswith('00:'):
            elapsed_str = elapsed_str[3:]

        self.printmsg(f' # {elapsed_str}s/it  --  Expected finish: {expected_end}')

    def write_checkpoint(self, iter_no, survivors, total_scores, scores,
                         metrics, foldings) -> None:
        ind = survivors[0]

        fields = [('iter_no', iter_no), ('mutation_rate', self.mutation_rate),
                  ('fitness', total_scores[ind])]
        fields.extend([
            ('metric:' + name, value)
            for name, value in sorted(metrics[ind].items())])
        fields.extend([
            ('score:' + name, value)
            for name, value in sorted(scores[ind].items())])
        fields.append(('seq', self.flatten_seqs[ind]))
        fields.append(('structure', foldings[ind]['folding']))

        if not self.checkpoint_header_written:
            header = [f[0] for f in fields]
            print(*header, sep='\t', file=self.checkpoint_file)
            self.checkpoint_header_written = True

        print(*[f[1] for f in fields], sep='\t', file=self.checkpoint_file)
        self.checkpoint_file.flush()

    def save_results(self):
        # Save the best sequence
        bestseq = ''.join(self.population[0])
        fastapath = os.path.join(self.outputdir, 'best-sequence.fasta')
        with open(fastapath, 'w') as f:
            print(f'>{self.seq_description}', file=f)
            print(*wrap(bestseq, width=self.fasta_line_width), sep='\n', file=f)

        # Save the parameters used for the optimization
        paramspath = os.path.join(self.outputdir, 'parameters.json')
        self.save_optimization_parameters(paramspath)

        # Prepare the evaluation results of the best sequence
        return {
            'initial': self.initial_sequence_evaluation,
            'optimized': self.seqeval.prepare_evaluation_data(bestseq)
        }

    def save_optimization_parameters(self, path: str) -> None:
        optdata = dump_to_preset(self.scoreopts, self.iteropts, self.execopts)
        open(path, 'w').write(optdata)
