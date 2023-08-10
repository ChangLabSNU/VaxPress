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

class ScoringFunction:

    name = 'noname'
    description = 'no description'

    # If True, the scoring function is called for each individual sequence.
    single_submission = False

    # Specifies the additional required arguments for the scoring function.
    requires = []

    # Command line arguments
    arguments = []

    @classmethod
    def add_argument_parser(cls, parser):
        grp = parser.add_argument_group('Fitness - ' + cls.description)
        argprefix = f'--{cls.name}-'
        argmap = []
        for argname, argopts in cls.arguments:
            grp.add_argument(argprefix + argname, **argopts)
            argmap.append((argprefix + argname, argname.replace('-', '_')))
        return argmap


def list_scoring_functions():
    from . import __path__, __name__
    import pkgutil, importlib

    funcs = {}

    for modinfo in pkgutil.iter_modules(__path__):
        modname = f'{__name__}.{modinfo.name}'
        mod = importlib.import_module(modname)

        for objname in dir(mod):
            obj = getattr(mod, objname)
            if (obj is not ScoringFunction and type(obj) == type and
                    issubclass(obj, ScoringFunction)):
                funcs[obj.name] = obj

    return funcs
