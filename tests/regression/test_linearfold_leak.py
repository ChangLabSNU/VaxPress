import linearfold
import os, psutil
from Bio import SeqIO

sequence = str(next(SeqIO.parse(open('test_rna1.fa'), 'fasta')).seq)
sequence = sequence.upper().replace('T', 'U')

process = psutil.Process()
get_memory_consumption = lambda: process.memory_info().rss

print('Memory usage before prediction:', get_memory_consumption() / 1024 / 1024, 'MB')

for i in range(100):
    linearfold.fold(sequence)
    print('[{}] {:.3f} MiB'.format(i+1, get_memory_consumption() / 1024 / 1024))
