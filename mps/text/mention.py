"""
The Mention class represents a mention in a document.
It is formed from a list of Word objects and keeps
track of the span of these words by saving the index
of the first and the last word. Mentions are sortable
by the index of their first word and can be evaluated
against other mentions:
    - equal (==): two mentions are equal if they
            have the same words and span
    - same surface: two mentions have the same
            surface if they are composed by the same
            words (all lower cased) but may have
            different spans
"""

import re

from mps.text.attributes import Attributes


class Mention:

    def __init__(self, words):
        self.span = (words[0].index, words[-1].index)
        self.words = words
        self.antecedent = False
        self.cluster = None
        self.next = None
        self.tree = None
        self.head = self.get_head(words)
        self.attributes = Attributes(self)

        if words[0].sentence == words[-1].sentence:
            self.sentence = words[0].sentence
        else:
            raise ValueError(
                "Mentions cannot span over multiple sentences"
            )

    def __eq__(self, other):
        """
        2 mentions are equal if they contain the same words
        """
        if self.words == other.words:
            return True
        return False

    def __lt__(self, other):
        """
        mentions are sorted by the span as a tuple
        """
        return self.span < other.span

    def __repr__(self):
        return " ".join(str(i) for i in (self.words))

    def __contains__(self, other):
        """
        a mention contains another one if the latter is embedded:
        [[the explosion] on the ship]
        """
        o_b, o_e = other.span
        if o_b >= self.span[0] and o_e <= self.span[1]:
            return True
        return False

    def __getitem__(self, index):
        return self.words[index]

    def get_head(self, words):
        """
        This function will extract the head of the NP.
        Naive Assumption: the head of the NP is
        the first noun in the mention
        """

        mention_tags = [i.tag for i in words]
        pattern = re.compile("NN")
        for i, tag in enumerate(mention_tags):
            found = re.match(pattern, tag)
            if found:
                return words[i]

        return None

    def same_surface(self, other):
        """
        2 mentions have the same surface if all the words have
        the same symbol (but may have different indexes)
        """
        # mentions with different length are different
        if len(self.words) != len(other.words):
            return False

        # return true if all words have the same surface
        if all(i.same_surface(j) for i, j in zip(self.words, other.words)):
            return True

        return False


if __name__ == "__main__":
    from mps.text.word import Word

    print("---DEMO: MENTION---")
    m1 = Mention([
        Word("the", 0, 0, "ART", None),
        Word("ship", 1, 0, "NN", None)
    ])

    m2 = Mention([
        Word("the", 0, 0, "ART", None),
        Word("ship", 1, 0, "NN", None),
        Word("in", 2, 0, "PRP", None),
        Word("Jakarta", 3, 0, "PNN", None)
    ])

    m3 = Mention([
        Word("the", 10, 2, "ART", None),
        Word("ship", 11, 2, "NN", None)
    ])

    print(
        "Mentions contains word objects and"
        "calculate attributes.\n"
        f"first mention (FM):\t{m1}, span: {m1.span}\n"
        f"second mention (SM):\t{m2}, span: {m2.span}\n"
        f"third mention (TM):\t{m3}, span: {m3.span}\n"
        "\nSome functions with mentions:\n"
        f"SM contains FM: {m1 in m2}\n"
        f"SM == TM: {m1 == m3}\n"
        f"SM same surface as TM: {m1.same_surface(m3)}\n"
        f"\nFinally attributes are also calculated:\n"
        f"{m1}: {m1.attributes}\n"
        f"{m2}: {m2.attributes}\n"
        f"{m3}: {m3.attributes}"
    )
