#!/usr/bin/env python
import pandas as pd
from datetime import datetime
from io import StringIO
import re
from textwrap import wrap
from urllib import request

SELECTED_SPECIES = [
    'Homo sapiens',
    'Mus musculus',
    'Rattus norvegicus',
    'Danio rerio',
    'Macaca mulatta',
]

DATA_URL = '\
https://dnahive.fda.gov/dna.cgi?cmd=objFile&ids=537&filename=Refseq_species.tsv&raw=1'

HEADER = """\
#
# Codon Frequency Table
#
# The data in this table is derived from the CoCoPUTs codon usage database [1].
# Automatically generated using tools/prepare-codon-usage.py on {now}.
#
# [1] Alexaki et al. (2019) Codon and Codon-Pair Usage Tables (CoCoPUTs):
#     facilitating genetic variation analyses and recombinant gene design.
#     Journal of Molecular Biology. 2019
#

codon_usage = {{}}
"""

def load_codon_table():
    print('Downloading', DATA_URL)
    print(' - This may take a while as the file size is over 100MB.')
    content = request.urlopen(DATA_URL).read().decode()
    print(' - done.')

    # CoCoPUTs tsv contains an excessive trailing tab
    content = content.replace('\t\n', '\n')

    table = pd.read_csv(StringIO(content), sep='\t')
    table = table[table['Species'].isin(SELECTED_SPECIES) &
                  (table['Organelle'] == 'genomic')]

    pat_codon = re.compile('[ACGT]{3}')
    codoncols = [col for col in table.columns if pat_codon.match(col)]
    assert len(codoncols) == 64

    subtable = table.set_index('Species')[codoncols].copy()
    return subtable.rename(mapper=lambda x: x.replace('T', 'U'), axis='columns')

def format_codon_table(table):
    formatted = []

    for species, codoncounts in table.iterrows():
        freqs = (codoncounts / codoncounts.sum()).round(6).to_dict()

        formatted.append(f"codon_usage['{species}'] = {{")
        formatted.extend(wrap(repr(freqs)[1:-1],
                              initial_indent='  ', subsequent_indent='  '))
        formatted.append('}\n')
    
    return '\n'.join(formatted)

if __name__ == '__main__':
    import sys
    import os
    script_path = os.path.abspath(sys.argv[0])
    output_path = os.path.dirname(script_path) + '/../vaxpress/codon_usage_data.py'

    with open(output_path, 'w') as out:
        table = load_codon_table()
        formatted = format_codon_table(table)
        print(HEADER.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), file=out)
        print(formatted, file=out, end='')
