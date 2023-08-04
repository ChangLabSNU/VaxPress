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
from tqdm import tqdm
from tabulate import tabulate
from collections import namedtuple
from concurrent import futures
from itertools import cycle
from .mutant_generator import MutantGenerator, STOP
from .scoring.icodon_stability import iCodonStabilityFitness
from .scoring.cai import CodonAdaptationIndexFitness
from .scoring.ucount import UridineCountFitness
from .scoring.gc_ratio import GCRatioFitness
from .scoring.folding import RNAFoldingFitness
from .scoring.tandem_repeats import TandemRepeatsFitness
from . import __version__

PROTEIN_ALPHABETS = 'ACDEFGHIKLMNPQRSTVWY' + STOP
RNA_ALPHABETS = 'ACGU'

fitness_scorefuncs = {
    'iCodon': iCodonStabilityFitness,
    'cai': CodonAdaptationIndexFitness,
    'ucount': UridineCountFitness,
    'gc': GCRatioFitness,
    'folding': RNAFoldingFitness,
    'repeats': TandemRepeatsFitness,
}

ScoringOptions = namedtuple('ScoringOptions', [
    # iCodon predicted stability
    'iCodon_weight',
    # Codon Adaptation Index
    'cai_weight',
    # U content
    'ucount_weight',
    # GC ratio
    'gc_weight', 'gc_window_size', 'gc_stride',
    # Secondary structure folding
    'folding_off', 'folding_engine', 'folding_mfe_weight',
    'folding_start_structure_width', 'folding_start_structure_weight',
    # Tandem repeats
    'repeats_min_repeats', 'repeats_repeat_length', 'repeats_weight',
])

IterationOptions = namedtuple('IterationOptions', [
    'n_iterations', 'n_offsprings', 'n_survivors', 'initial_mutation_rate',
    'winddown_trigger', 'winddown_rate'
])

ExecutionOptions = namedtuple('ExecutionOptions', [
    'seed', 'processes', 'random_initialization', 'species', 'codon_table',
    'protein', 'quiet', 'seq_description', 'print_top_mutants'
])

class CDSEvolutionChamber:

    hbar = '-' * 80
    finalized_seqs = None
    stop_threshold = 0.2

    def __init__(self, cdsseq: str, checkpoint_output: str, scoring_options: ScoringOptions,
                 iteration_options: IterationOptions, exec_options: ExecutionOptions):
        self.cdsseq = cdsseq.upper()

        self.seq_description = exec_options.seq_description
        self.checkpoint_path = checkpoint_output
        self.scoreopts = scoring_options
        self.iteropts = iteration_options
        self.execopts = exec_options
        self.n_processes = exec_options.processes
        self.quiet = exec_options.quiet
        self.print_top_mutants = exec_options.print_top_mutants

        self.initialize()

    def printmsg(self, *args, **kwargs) -> None:
        if not self.quiet:
            kwargs['file'] = sys.stderr
            print(*args, **kwargs)

    def initialize(self) -> None:
        if self.execopts.protein:
            invalid_letters = set(self.cdsseq) - set(PROTEIN_ALPHABETS)
            if invalid_letters:
                raise ValueError(f'Invalid protein sequence: {" ".join(invalid_letters)}')
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
                                         self.execopts.protein)
        if self.execopts.random_initialization or self.execopts.protein:
            self.mutantgen.randomize_initial_codons()
        self.population = [self.mutantgen.initial_codons]

        self.mutation_rate = self.iteropts.initial_mutation_rate

        self.length_aa = len(self.population[0])
        self.length_cds = len(self.cdsseq)

        self.initialize_fitness_scorefuncs()

        self.best_scores = []
        self.elapsed_times = []
        self.checkpoint_file = open(self.checkpoint_path, 'w')
        self.checkpoint_header_written = False

    def initialize_fitness_scorefuncs(self) -> None:
        self.scorefuncs_single = []
        self.scorefuncs_batch = []

        additional_opts = {
            'length_cds': self.length_cds,
        }

        for funcname, cls in fitness_scorefuncs.items():
            opts = {k[len(funcname)+1:]: v for k, v
                    in self.scoreopts._asdict().items()
                    if k.startswith(funcname + '_')}
            if ('weight' in opts and opts['weight'] == 0) or ('off' in opts and opts['off']):
                continue
            opts.update(additional_opts)
            for reqattr in cls.requires:
                opts[reqattr] = getattr(self, reqattr)

            scorefunc_inst = cls(**opts)
            if cls.single_submission:
                self.scorefuncs_single.append(scorefunc_inst)
            else:
                self.scorefuncs_batch.append(scorefunc_inst)

    def show_configuration(self) -> None:
        spec = self.mutantgen.compute_mutational_space()

        self.printmsg(f'VaxPress Codon Optimizer for mRNA Vaccines {__version__}')
        self.printmsg('=' * len(self.hbar))
        self.printmsg(f' * Name: {self.seq_description}')
        self.printmsg(f' * CDS length: {self.length_cds} nt')
        self.printmsg(f' * Possible single mutations: {spec["singles"]}')
        self.printmsg(f' * Possible sequences: {spec["total"]}')
        self.printmsg()

    def mutate_population(self) -> None:
        nextgeneration = self.population[:]

        n_new_mutants = max(0, self.iteropts.n_offsprings - len(self.population))
        for parent, _ in zip(cycle(self.population), range(n_new_mutants)):
            child = self.mutantgen.generate_mutant(parent, self.mutation_rate)
            nextgeneration.append(child)

        self.population[:] = nextgeneration
        self.flatten_seqs = [''.join(p) for p in self.population]

    def evaluate_population(self, executor) -> None:
        scores = [{} for i in range(len(self.population))]
        metrics = [{} for i in range(len(self.population))]

        def collect_scores_batch(future):
            scoreupdates, metricupdates = future.result()
            pbar.update()

            # Update scores
            for k, updates in scoreupdates.items():
                assert len(updates) == len(scores)
                for s, u in zip(scores, updates):
                    s[k] = u

            # Update metrics
            for k, updates in metricupdates.items():
                assert len(updates) == len(metrics)
                for s, u in zip(metrics, updates):
                    s[k] = u

        def collect_scores_single(future):
            scoreupdates, metricupdates = future.result()
            i = future._seqidx
            scores[i].update(scoreupdates)
            metrics[i].update(metricupdates)
            pbar.update()

        num_tasks = len(self.scorefuncs_batch) + len(self.scorefuncs_single) * len(self.flatten_seqs)
        self.printmsg('')
        pbar = tqdm(total=num_tasks, disable=self.quiet, file=sys.stderr,
                    unit='task', desc='Scoring fitness')
        jobs = []
        for scorefunc in self.scorefuncs_batch:
            future = executor.submit(scorefunc, self.flatten_seqs)
            future.add_done_callback(collect_scores_batch)
            jobs.append(future)

        for scorefunc in self.scorefuncs_single:
            for i, seq in enumerate(self.flatten_seqs):
                future = executor.submit(scorefunc, seq)
                future._seqidx = i
                future.add_done_callback(collect_scores_single)
                jobs.append(future)

        futures.wait(jobs)
        pbar.close()
        self.printmsg('')

        total_scores = [sum(s.values()) for s in scores]

        return total_scores, scores, metrics

    def run(self) -> None:
        if not self.quiet:
            self.show_configuration()

        n_survivors = self.iteropts.n_survivors
        last_winddown = 0

        with futures.ProcessPoolExecutor(max_workers=self.n_processes) as executor:
            for i in range(self.iteropts.n_iterations):
                iter_no = i + 1
                n_parents = len(self.population)

                self.expected_total_mutations = (
                    self.mutantgen.compute_expected_mutations(self.mutation_rate))
                if self.expected_total_mutations < self.stop_threshold:
                    self.printmsg('==> Stopping: expected mutation reaches the minimum')
                    break

                iteration_start = time.time()

                self.printmsg(self.hbar)
                self.printmsg(f'Iteration {iter_no}/{self.iteropts.n_iterations}  --',
                              f'  mut_rate: {self.mutation_rate:.5f} --',
                              f'E(muts): {self.expected_total_mutations:.1f}')

                self.mutate_population()
                total_scores, scores, metrics = self.evaluate_population(executor)

                ind_sorted = np.argsort(total_scores)[::-1]
                survivors = [self.population[i] for i in ind_sorted[:n_survivors]]
                self.best_scores.append(total_scores[ind_sorted[0]])

                self.print_eval_results(total_scores, metrics, ind_sorted, n_parents)
                self.write_checkpoint(iter_no, ind_sorted[:n_survivors], total_scores,
                                      scores, metrics)

                self.population[:] = survivors

                self.printmsg(f' # Last best scores:',
                              ' '.join(f'{s:.3f}' for s in self.best_scores[-5:]))
                if (len(self.best_scores) >= self.iteropts.winddown_trigger and
                        iter_no - last_winddown > self.iteropts.winddown_trigger):
                    if self.best_scores[-1] <= self.best_scores[-self.iteropts.winddown_trigger]:
                        self.mutation_rate *= self.iteropts.winddown_rate
                        self.printmsg(f'==> Winddown triggered: mutation rate = {self.mutation_rate:.5f}')
                        last_winddown = iter_no

                iteration_end = time.time()

                self.print_time_estimation(iteration_start, iteration_end, iter_no)

                self.printmsg()

    def print_eval_results(self, total_scores, metrics, ind_sorted, n_parents) -> None:
        if self.quiet:
            return

        print_top = min(self.print_top_mutants, len(self.population))
        rowstoshow = ind_sorted[:print_top]
        if len(rowstoshow) < 1:
            return

        header = ['flags', 'score'] + sorted(metrics[rowstoshow[0]].keys())
        tabdata = []
        for rank, i in enumerate(rowstoshow):
            is_parent = 'P' if i < n_parents else '-'
            is_survivor = 'S' if rank < self.iteropts.n_survivors else '-'
            f_total = total_scores[i]
            f_metrics = [metrics[i][name] for name in header[2:]]
            tabdata.append([is_parent + is_survivor, f_total] +f_metrics)

        self.printmsg(tabulate(tabdata, header, tablefmt='simple', floatfmt='.2f'), end='\n\n')

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

    def write_checkpoint(self, iter_no, survivors, total_scores, scores, metrics) -> None:
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

        if not self.checkpoint_header_written:
            header = [f[0] for f in fields]
            print(*header, sep='\t', file=self.checkpoint_file)
            self.checkpoint_header_written = True

        print(*[f[1] for f in fields], sep='\t', file=self.checkpoint_file)
        self.checkpoint_file.flush()

if __name__ == '__main__':
    pass
