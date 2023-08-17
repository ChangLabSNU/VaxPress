# Example code to optimize sequences to have a specific restriction enzyme recognition site.
# IUPAC ambiguity codes are not supported.

from vaxpress.scoring import ScoringFunction

class RestrictionSiteFitness(ScoringFunction):

    # If True, the scoring function is called for each individual sequence.
    single_submission = False

    name = 'resite'                    # used as an argument prefix, e.g. "--resite-weight"
    description = 'Restriction Site'   # Description shown in help message
    priority = 100                     # Affects the order in which the scoring function is displayed in the help message
    
    # Define arguments for your scoring function here.
    arguments = [
        ('weight', dict(
            type=float, default=10.0,  # set high default weight to firmly select sequences with the restriction site
            help='scoring weight for the presence of the restriction site (default: 10.0)')),
        ('restriction-site', dict(
            default=None, type=str, help='restriction site sequence containing only A, C, G, T or U (default: None)')),
    ]

    # Initialize the scoring function with the given arguments.
    def __init__(self, weight, restriction_site, _length_cds):  
        
        self.weight = weight
        self.restriction_site = restriction_site
        if self.restriction_site is None:
            raise ValueError('restriction site sequence is not specified')
    
        self.restriction_site = self.restriction_site.replace('T', 'U').upper()
        if set(self.restriction_site)-set('ACGU'):
            raise ValueError('restriction site contains invalid characters')

    # This is where your code for calculating desired metrics & scores goes. 
    def score(self, seqs):  
     
        is_site = []    # Initialize list to store 0 or 1 for each sequence.
        scores = []     # Initialize list to store the final score for each sequence.

        for seq in seqs:
            # If the sequence contains the restriction site, gives 1
            if self.restriction_site in seq:
                is_site.append(1)  
            # If the sequence does not contain the restriction site, gives 0
            else:
                is_site.append(0) 
            
        for v in is_site:
            scores.append(v * self.weight) 
        
        # Return scores and metrics
        return {'resite': scores}, {'resite': is_site}