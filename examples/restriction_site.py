# Example code that optimizes a sequence to have a specific restriction enzyme
# recognition site.

from vaxpress.scoring import ScoringFunction

class RestrictionSiteFitness(ScoringFunction):

    # True: The scoring function is called with each sequence individually.
    #       This is useful if the scoring function is computationally expensive.
    # False: The scoring function is called with all sequences at once.
    #        This is useful if the scoring function is fast or memory-intensive.
    single_submission = False

    # Prefix in command line arguments, e.g. "--resite-weight"
    name = 'resite'

    # Appears in the help message
    description = 'Restriction Site'

    # Adjusts the order of appearance in the help message. Lower numbers appear
    # first.
    priority = 100

    # Definitions for command line arguments.
    arguments = [
        ('weight', dict(
            type=float,
            default=10.0, # penalize for the violations
            help='scoring weight for the presence of the restriction site '
                 '(default: 10.0)')),
        ('restriction-site', dict(
            default=None, type=str,
            help='restriction site sequence containing only A, C, G, T or '
                 'U (default: None)')),
    ]

    # Argument "_length_cds" is always passed to the constructor. Leave it as
    # it is even if you don't use it.
    def __init__(self, weight, restriction_site, _length_cds):
        self.weight = weight
        self.restriction_site = restriction_site
        if self.restriction_site is None:
            raise EOFError # disable this scoring function

        self.restriction_site = self.restriction_site.upper().replace('T', 'U')
        if set(self.restriction_site) - set('ACGU'):
            raise ValueError('restriction site contains invalid characters')

    # This function is called for every iteration. "seqs" is a list of strings
    # if single_submission is False, or a single string if single_submission is
    # True.
    def score(self, seqs):
        has_site = [] # 0s or 1s indicating existence of site for each sequence.
        scores = [] # fitness values for each sequences. Higher is better.

        for seq in seqs:
            if self.restriction_site in seq:
                found = 1
            else:
                found = 0

            has_site.append(found)
            scores.append(found * self.weight)

        # The first dict should contain the fitness values for each sequence.
        # The second dict may contain the original metrics for it for reference.
        return {'resite': scores}, {'resite': has_site}
