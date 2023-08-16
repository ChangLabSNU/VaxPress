# Example code for counting homopolymers as units of trimers

from vaxpress.scoring import ScoringFunction

class HomopolymerFitness(ScoringFunction):

    single_submission = False

    name = "homopolymer"
    description = "Homopolymer Count"
    priority = 110 

    arguments = [
        ('weight', dict(
            type=float, default=1.0,
            help='scoring weight for homopolymer count (default: 1.0)')),
    ]

    def __init__(self, weight, _length_cds):
        self.weight = -weight / _length_cds 

    def score(self, seqs):
        counts = []
        scores = []
        for s in seqs: 
            hcount = s.count('AAA') + s.count('CCC') + s.count('GGG') + s.count('TTT')
            counts.append(hcount)
            scores.append(hcount * self.weight)
        return {'homopolymer': scores}, {'homopolymer': counts}