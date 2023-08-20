# Example code for counting the number of trimers consisted of the consecutive
# same bases

from vaxpress.scoring import ScoringFunction

class HomoTrimerFitness(ScoringFunction):

    single_submission = False

    name = 'homotrimer'
    description = 'Homotrimer Count'
    priority = 110

    arguments = [
        ('weight', dict(
            type=float, default=1.0,
            help='scoring weight for homotrimer count (default: 1.0)')),
    ]

    def __init__(self, weight, _length_cds):
        self.weight = -weight / _length_cds

    def score(self, seqs):
        counts = []
        scores = []
        for seq in seqs:
            hcount = (seq.count('AAA') + seq.count('CCC') +
                      seq.count('GGG') + seq.count('TTT'))
            counts.append(hcount)
            scores.append(hcount * self.weight)
        return {'homotrimer': scores}, {'homotrimer': counts}
