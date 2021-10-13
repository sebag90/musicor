"""
This sieve will try to match only pronouns with other
mentions based on a series of attributes:
    - genus
    - number
    - animacy
    - person
"""

from mps.sieves.template import Sieve


class Pronoun(Sieve):

    pronouns = {
        "I", "me",
        "you",
        "he", "him",
        "she", "her",
        "they", "them",
        "we", "us"
    }

    def process(self, document, clusters):
        for mention in clusters:
            if mention.antecedent is False:
                if (len(mention.words) == 1 and
                        mention.words[0].symbol.lower() in self.pronouns):
                    # prune mentions
                    pruned = self.prune(mention)
                    if not pruned:
                        # collect candidates
                        candidates = clusters.get_candidates(
                            mention, document, pronoun=True
                        )

                        # look for matches
                        for candidate in candidates:
                            # obtain cluster attributes
                            ma = clusters.attributes[mention.cluster]
                            ca = clusters.attributes[candidate.cluster]

                            if ma.is_subset(ca):
                                clusters.merge(mention, candidate)
                                break

        return clusters
