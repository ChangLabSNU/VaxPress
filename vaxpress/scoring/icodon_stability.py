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

from . import ScoringFunction

class iCodonStabilityFitness(ScoringFunction):

    iCodon_initialized = False
    single_submission = False
    predfuncs = {} # cache for iCodon predict_stability functions

    name = 'iCodon'

    def __init__(self, weight, species, length_cds):
        self.weight = weight
        self.species = species
        self.length_cds = length_cds

    def __call__(self, seqs):
        if not self.iCodon_initialized:
            import os
            os.environ['TZ'] = 'UTC' # dplyr requires this to run in singularity

            import rpy2.robjects.packages as rpackages
            rpackages.importr('iCodon')
            rpackages.importr('stringr')

            import rpy2.robjects as ro
            ro.r['options'](warn=-1)

            self.iCodon_initialized = True

        import rpy2.robjects as ro
        if self.species not in self.predfuncs:
            self.predfuncs[self.species] = ro.r['predict_stability'](self.species)

        pred = self.predfuncs[self.species](seqs)
        pred = list(map(float, pred))
        scores = [s * self.weight for s in pred]
        return {'pred_stability': scores}, {'pred_stability': pred}
