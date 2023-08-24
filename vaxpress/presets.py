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

import json

execopts_to_remove = [
    'output', 'overwrite', 'quiet', 'seq_description', 'print_top_mutants',
    'protein']
iteroptions_aliases = {
    'n_iterations': 'iterations',
    'n_offsprings': 'offsprings',
    'n_survivors': 'survivors',
    'lineardesign_lambda': 'lineardesign',
}

def dump_to_preset(scoreopts, iteropts, execopts):
    data = {}

    data.update(iteropts._asdict())
    data.update({k: v for k, v in execopts._asdict().items()
                 if k not in execopts_to_remove})

    data['fitness'] = {}
    for modname, args in scoreopts.items():
        mod = data['fitness'][modname] = {}
        for argname, argval in args.items():
            if not argname.startswith('_'):
                mod[argname] = argval

    return json.dumps(data, indent=2)

def load_preset(data):
    return {
        iteroptions_aliases.get(k, k): v
        for k, v in json.loads(data).items()
    }
