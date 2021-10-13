"""
The exact match sieve connects two mentions
if they have the same words (different casing
is allowed.
"""

from mps.sieves.template import Sieve


class ExactMatch(Sieve):

    def process(self, document, clusters):
        """
        Loop over the mentions, if a mention does not
        have an antecedent, loop with an inner loop from
        the beginning until the selected mention (cataphoric
        chains are not allowed) if two mentions have the same
        surface, merge the clusters
        """
        for mention in clusters:
            if mention.antecedent is False:

                # collect candidates
                candidates = clusters.get_candidates(mention, document)

                # look for matches
                for candidate in candidates:
                    if mention.same_surface(candidate):
                        clusters.merge(mention, candidate)
                        break

        return clusters
