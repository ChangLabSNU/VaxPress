#
# VaxPress
#
# Copyright 2023 Seoul National University
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
import os

ARGUMENTS_AUTOMATIC_SAVE = ['lineardesign_dir']

default_configfile = os.path.join(
    os.path.expanduser('~'), '.config', 'vaxpress', 'config.json')

def load_config(configfile=default_configfile):
    try:
        return json.load(open(configfile))
    except (FileNotFoundError, PermissionError):
        return {}

def initialize_config_if_needed(args, configfile=default_configfile):
    conf = load_config(configfile)

    modified = False
    for k in ARGUMENTS_AUTOMATIC_SAVE:
        newvalue = getattr(args, k)
        if newvalue is not None and conf.get(k) != newvalue:
            conf[k] = newvalue
            modified = True

    if not modified:
        return

    try:
        os.makedirs(os.path.dirname(configfile), exist_ok=True)
        json.dump(conf, open(configfile, 'w'), indent=2)
    except (PermissionError, FileExistsError):
        pass
