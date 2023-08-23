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

import os
import subprocess as sp

def run_lineardesign(lineardesign_dir, sequence, lmd=0.5,
                     codonusage='codon_usage_freq_table_human.csv'):
    lineardesign_bin = os.path.join(lineardesign_dir, 'bin/LinearDesign_2D')
    lineardesign_bin = os.path.abspath(lineardesign_bin)
    if not os.path.exists(lineardesign_bin):
        raise FileNotFoundError(f'LinearDesign binary not found in {lineardesign_dir}')

    with sp.Popen([lineardesign_bin, str(lmd), '0', codonusage],
                  cwd=lineardesign_dir, stdin=sp.PIPE, stdout=sp.PIPE) as proc:
        proc.stdin.write(sequence.encode())
        proc.stdin.write(b'\n')
        proc.stdin.close()

        ret = proc.stdout.read().decode()

    if 'mRNA sequence:  ' not in ret:
        raise ValueError('Unexpected output from LinearDesign.')

    lines = ret.split('mRNA sequence:  ')[1].splitlines()
    rnaseq = lines[0].strip()
    rnastr = lines[1].split(': ')[1].strip()
    mfe = float(lines[2].split(': ')[1].split()[0])
    cai = float(lines[2].split(': ')[2].strip())

    return {
        'seq': rnaseq,
        'str': rnastr,
        'mfe': mfe,
        'cai': cai,
    }
