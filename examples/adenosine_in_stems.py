from vaxpress.scoring import ScoringFunction

class AdenosineInStemFitness(ScoringFunction):

    name = 'paired_a'
    description = 'Adenosines in Double-Stranded Region'
    priority = 100
    uses_folding = True

    arguments = [
        ('weight', dict(metavar='WEIGHT',
            type=float, default=-10.0,
            help='score for adenosine in dsRNA regions (default: -10.0)')),
        ('threshold', dict(
            type=int, default=10, metavar='N',
            help='minimum length of dsRNA stem to consider (default: 10)')),
    ]

    penalty_metric_flags = {}

    def __init__(self, threshold, weight, _length_cds):
        self.threshold = threshold
        self.weight = weight / _length_cds * 100

    def score(self, seqs, foldings):
        metrics = []
        scores = []

        total_count = 0

        for seq, fold in zip(seqs, foldings):
            stems = fold['stems']
            for loc5, loc3 in stems:
                if len(loc5) < self.threshold:
                    continue

                seq5 = seq[loc5[0]:loc5[-1]+1]
                seq3 = seq[loc3[0]:loc3[-1]+1]
                total_count += seq5.count('A') + seq3.count('A')

            metrics.append(total_count)
            scores.append(total_count * self.weight)

        return {'paired_a': scores}, {'paired_a': metrics}

    def annotate_sequence(self, seq, folding):
        stems = folding['stems']
        total_count = 0
        for loc5, loc3 in stems:
            if len(loc5) >= self.threshold:
                seq5 = seq[loc5[0]:loc5[-1]+1]
                seq3 = seq[loc3[0]:loc3[-1]+1]
                total_count += seq5.count('A') + seq3.count('A')
        return {'paired_a': total_count}
