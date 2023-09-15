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

from . import ScoringFunction

ICODON_SPECIES_MAPPING = {
    'Homo sapiens': 'human',
    'Mus musculus': 'mouse',
    'Danio rerio': 'zebrafish',
}

def check_iCodon_availability(kls):
    try:
        import rpy2.robjects.packages as rpackages
    except ModuleNotFoundError:
        return

    try:
        rpackages.importr('iCodon')
    except rpackages.PackageNotInstalledError:
        return

    return kls

@check_iCodon_availability
class iCodonStabilityFitness(ScoringFunction):

    iCodon_initialized = False
    predfunc = None

    name = 'iCodon'
    description = 'iCodon'
    priority = 10

    requires = ['species']
    arguments = [
        ('weight', dict(
            type=float, default=1.0, metavar='WEIGHT',
            help='scoring weight for iCodon predicted stability (default: 1.0)')),
    ]

    def __init__(self, weight, _species, _length_cds):
        self.weight = weight
        if _species not in ICODON_SPECIES_MAPPING:
            raise ValueError(f"Unsupported species by iCodon: {_species}")
        self.species = ICODON_SPECIES_MAPPING[_species]
        self.length_cds = _length_cds

    def score(self, seqs):
        if not self.iCodon_initialized:
            import os
            os.environ['TZ'] = 'UTC' # dplyr requires this to run in singularity

            import rpy2.robjects.packages as rpackages
            rpackages.importr('iCodon')
            rpackages.importr('stringr')

            import rpy2.robjects as ro
            ro.r['options'](warn=-1)
            self.predfunc = ro.r['predict_stability'](self.species)

            self.iCodon_initialized = True

        # Remove duplicates since iCodon refuses prediction of sequence lists
        # containing duplicates
        query = list(set(seqs))
        results = self.predfunc(query)
        results = dict(zip(query, results))

        pred = [float(results[s]) for s in seqs]
        scores = [s * self.weight for s in pred]
        return {'pred_stability': scores}, {'pred_stability': pred}
