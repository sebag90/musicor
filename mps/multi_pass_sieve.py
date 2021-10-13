"""
Main class of the multi pass sieve. Sieves are implemented
singularly in the sieves/ directory. To add a new sieve,
import it here and add it to the self.available dictionary
"""

from mps.sieves.exact_match_sieve import ExactMatch
from mps.sieves.precise_constructs_sieve import PreciseConstructs
from mps.sieves.pronoun_sieve import Pronoun
from mps.text.cluster_container import ClusterContainer
from mps.utils.errors import MissingSieve


class MultiPassSieve:

    def __init__(self, sieves):
        self.available = {
            "ExactMatch": ExactMatch(),
            "PreciseConstructs": PreciseConstructs(),
            "Pronoun": Pronoun()
        }

        # if a sieve is not implemented
        # raise a MissingSieve error
        if any(sieve not in self.available.keys() for sieve in sieves):
            raise MissingSieve(
                "Sieve not implemented or recognized\n"
                f"Available Sieves: {', '.join(self.available.keys())}"
            )

        # create a list of Sieve-objects
        self.sieves = [
            self.available[i] for i in sieves
        ]

    def __call__(self, document):
        # get mentions from document
        mentions = document.nps

        # mentions are saved in a ClusterContainer
        # and passed on to each sieve
        clusters = ClusterContainer(mentions)

        for sieve in self.sieves:
            clusters = sieve(document, clusters)

        return clusters
