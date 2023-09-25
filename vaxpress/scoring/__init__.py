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

import abc

class ScoringFunction(abc.ABC):

    name = 'noname'
    description = 'no description'

    # Command line help shows in ascending order of this priority
    priority = 99

    # If True, score() method is called with a list of folding predictions.
    uses_folding = False

    # If True, annotate_sequence() or evaluate_local() is called even when
    # the weight is zero.
    use_annotation_on_zero_weight = False

    # Specifies the additional required arguments for the constructor
    requires = []

    # Command line arguments
    arguments = []

    # One letter flags for showing penalty metrics in the console.
    penalty_metric_flags = {}

    @classmethod
    def add_argument_parser(cls, parser):
        grp = parser.add_argument_group('Fitness - ' + cls.description)
        argprefix = '--{name}-'.format(name=cls.name.replace('_', '-'))
        argmap = []
        for argname, argopts in cls.arguments:
            grp.add_argument(argprefix + argname, **argopts)
            argmap.append((argprefix + argname, argname.replace('-', '_')))
        return argmap

    def __call__(self, seqs, *args, **kwargs):
        try:
            return self.score(seqs, *args, **kwargs)
        except KeyboardInterrupt:
            return None

    @abc.abstractmethod
    def score(self, seqs):
        raise NotImplementedError

def discover_scoring_functions(addon_paths):
    from . import __path__, __name__
    import pkgutil
    import importlib
    import os
    import sys

    funcs = {}

    def scan_module(mod):
        for objname in dir(mod):
            obj = getattr(mod, objname)
            if (obj is not ScoringFunction and type(obj) == abc.ABCMeta and
                    issubclass(obj, ScoringFunction)):
                funcs[obj.name] = obj

    for modinfo in pkgutil.iter_modules(__path__):
        modname = f'{__name__}.{modinfo.name}'
        mod = importlib.import_module(modname)
        scan_module(mod)

    loaded = set()
    for filepath in addon_paths:
        # It is tricky to load the addon module from each individual file because
        # multiprocessing requires the functions are importable using the module
        # path in sys.path. So we add the addon path to sys.path and load it using
        # the name.
        modname = os.path.splitext(os.path.basename(filepath))[0]
        abspath = os.path.abspath(filepath)
        if abspath in loaded:
            continue
        loaded.add(abspath)

        dirname = os.path.dirname(abspath)
        if dirname not in sys.path:
            sys.path.insert(0, os.path.dirname(abspath))
        mod = importlib.import_module(modname)
        scan_module(mod)

    return funcs
