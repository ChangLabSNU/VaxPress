#!/usr/bin/env python
import pandas as pd
from datetime import datetime
from urllib import request
from itertools import product
from base64 import a85encode
import numpy as np

SELECTED_SPECIES = [
    'Homo sapiens',
    'Mus musculus',
    'Rattus norvegicus',
    'Danio rerio',
    'Macaca mulatta',
]

DATA_URL = '\
https://dnahive.fda.gov/dna.cgi?cmd=objFile&ids=537&filename=Refseq_Bicod.tsv&raw=1'
FILENAME = 'Refseq_Bicod.tsv'

WRAPLINE = 80

HEADER = """\
#
# Bicodon Frequency Table
#
# The data in this table is derived from the CoCoPUTs codon usage database [1].
# Automatically generated using tools/prepare-bicodon-usage.py on {now}.
#
# [1] Alexaki et al. (2019) Codon and Codon-Pair Usage Tables (CoCoPUTs):
#     facilitating genetic variation analyses and recombinant gene design.
#     Journal of Molecular Biology. 2019
#

import numpy as np
from base64 import a85decode

def _(b):
    return np.frombuffer(a85decode(b), dtype=np.float16)

bicodon_usage = {{}}
"""

FOOTER = """\
"""

def load_codon_table():
    rows = []
    for chunk in pd.read_csv(FILENAME, sep='\t', low_memory=False, chunksize=10000):
        sel = chunk[chunk['Species'].isin(SELECTED_SPECIES) &
                    (chunk['Organelle'] == 'genomic')]
        if len(sel) > 0:
            rows.append(sel)

    return pd.concat(rows)

def process_codon_table(table):
    from Bio.Data import CodonTable

    codon2aa = CodonTable.standard_dna_table.forward_table.copy()
    codon2aa['TAA'] = codon2aa['TAG'] = codon2aa['TGA'] = '*'
    hexamers = [''.join(seq) for seq in product('acgt', repeat=6)]

    w_ret = {}

    for _, row in table.iterrows():
        bicodcnts = row[hexamers].to_frame('count').reset_index()
        bicodcnts['count'] = bicodcnts['count'].astype(int)
        bicodcnts['index'] = bicodcnts['index'].str.upper()
        bicodcnts['aa2'] = bicodcnts['index'].apply(
            lambda x: codon2aa[x[:3]] + codon2aa[x[3:]])
        bicodcnts['maxcount'] = -1
        for _, grp in bicodcnts.groupby('aa2'):
            bicodcnts.loc[grp.index, 'maxcount'] = grp['count'].max()
        bicodcnts['log_w'] = np.log(bicodcnts['count'] / bicodcnts['maxcount'])
        bicodcnts = bicodcnts.sort_values(by='index')
        assert len(bicodcnts) == 4096

        log_w = bicodcnts['log_w']
        w_noninf = log_w[~np.isinf(log_w)]
        normw = ((log_w - w_noninf.mean()) / w_noninf.std()).values

        w_ret[row['Species']] = normw

    return w_ret

def format_codon_table(w_lists):
    formatted = []

    for species, wscores in w_lists.items():
        wenc = a85encode(wscores.astype(np.float16).tobytes(), wrapcol=WRAPLINE)

        formatted.append(f"bicodon_usage['{species}'] = _(rb'''")
        formatted.append(wenc.decode() + "''')\n")

    return '\n'.join(formatted)

if __name__ == '__main__':
    import sys
    import os
    script_path = os.path.abspath(sys.argv[0])
    output_path = (
        os.path.dirname(script_path) +
        '/../vaxpress/data/bicodon_usage_data.py')

    if not os.path.exists(FILENAME):
        request.urlretrieve(DATA_URL, FILENAME)

    with open(output_path, 'w') as out:
        tbl = load_codon_table()
        w_lists = process_codon_table(tbl)
        formatted = format_codon_table(w_lists)
        print(HEADER.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), file=out)
        print(formatted, file=out, end='')
        print(FOOTER, file=out)
