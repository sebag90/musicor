"""
The precise constructs sieve will link 2 mentions if:
    - one is the acronym of the other
        ex. [NBC] ... [Nakahama Broadcast Corporation]

    - the second mention is an apposition of the first:
        ex.  [The prince of Zamunda], [Akeem Joffer], arrived ...

    - the second mention is a predicate of the first:
        ex. [Holland] is [the Netherlands]

    - the second mention is the head of the first:
        ex. [[the mutinous crew] of the HMS Bounty]
"""

from nltk.tree import Tree

from mps.sieves.template import Sieve
from mps.text.mention import Mention


class PreciseConstructs(Sieve):

    def __init__(self):
        self.document = None

    def __is_acronym(self, string1, string2):
        """
        returns true if string1 is the acronym
        of string2
        """
        string2 = string2.split()
        string2 = [i[0] for i in string2]
        if string1 == "".join(string2):
            return True
        return False

    def __apposition(self, mention, candidate):
        """
        checks if mention i if the apposition
        of mention j. To be true mention i must
        come right after mention j and be encapsulated
        in commas
        """
        init_i = mention.span[0]
        init_j = candidate.span[0]

        if init_i - 2 == init_j:
            if (self.document.tokens[init_i - 1] == "," and
                    self.document.tokens[init_i + 1] == ","):
                return True

        return False

    def __pred_nom(self, mention, candidate):
        """
        checks if mention i is the predicate of mention j.
        To be true, there must be an inflection of the verb
        to be between mention j and mention i
        """
        init_i = mention.span[0]
        init_j = candidate.span[0]

        if init_i - 2 == init_j:
            verb = self.document.tokens[init_i - 1].lower()
            if verb in {"is", "are", "am", "was", "were"}:
                return True

        return False

    def __acronym(self, mention, candidate):
        """
        Checks whether one of the mentions if the acronym
        of the other one. In order to return true, both
        mentions must be annotated with the NNP tag
        """
        init_i, end_i = mention.span
        span_i = slice(init_i, end_i + 1)
        tags_i_mentions = set(self.document.pos_tags[span_i])

        init_j, end_j = candidate.span
        span_j = slice(init_j, end_j + 1)
        tags_j_mentions = set(self.document.pos_tags[span_j])

        if tags_i_mentions == tags_j_mentions == set(["NNP"]):
            string1 = str(mention)
            string2 = str(candidate)
            acr1 = self.__is_acronym(string1, string2)
            acr2 = self.__is_acronym(string2, string1)

            if acr1 or acr2:
                return True

        return False

    def __get_NP_head(self, mention):
        """
        given a Mention-object, this function
        will extract the head of the NP
        """

        # assumption: the head is the first subtree
        head = mention.tree[0]

        if isinstance(head, Tree):
            # a head must be a NP itself
            if head.label() == "NP":
                head = head.leaves()
                return head

        return None

    def __is_head_of(self, mention, candidate):
        head = self.__get_NP_head(mention)
        if head:
            if Mention(head) == candidate:
                return True

        return False

    def process(self, document, clusters):
        self.document = document

        for mention in clusters:
            if mention.antecedent is False:
                pruned = self.prune(mention)  # prune mentions
                if not pruned:

                    # collect candidates
                    candidates = clusters.get_candidates(mention, document)

                    # look for matches
                    for candidate in candidates:
                        appo = self.__apposition(mention, candidate)
                        pred_nom = self.__pred_nom(mention, candidate)
                        akr = self.__acronym(mention, candidate)
                        head = self.__is_head_of(mention, candidate)

                        if (appo or pred_nom or akr or head):
                            clusters.merge(mention, candidate)
                            break

        return clusters
