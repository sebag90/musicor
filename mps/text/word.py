"""
the  word class substitutes words (strings)
for the tree representation. This way it
is possible to keep track of the indexes of
words once they are in the tree representation
Word-objects can be evaluated against each other:
    - equal (==): two words are equal if they
            have the same symbol and index
    - same surface: two words have the same
            surface if they have the same
            symbol (lower cased) but may have
            different indexes
"""


class Word:

    def __init__(self, symbol, index, sentence, tag, ne):
        self.symbol = symbol
        self.index = index
        self.sentence = sentence
        self.tag = tag
        self.ne = ne

    def __repr__(self):
        return self.symbol

    def __eq__(self, other):
        if (self.symbol == str(other) and
                self.index == other.index):
            return True
        return False

    def __lt__(self, other):
        if isinstance(other, Word):
            return self.index < other.index
        # TODO: restrict to int
        # otherwise error not implemented
        return self.index < other

    def same_surface(self, other):
        """
        returns true if two words have the same symbols (lower cased)
        """
        if self.symbol.lower() == other.symbol.lower():
            return True
        return False


if __name__ == "__main__":
    words = [
        Word("These", 0, 0, "PRN", None),
        Word("are", 1, 0, "VRB", None),
        Word("some", 2, 0, "QTNF", None),
        Word("words", 3, 0, "NNS", "ABS-ITEMS")
    ]

    print(
        "---DEMO: WORD---\n"
        f"list of word-objects: {words}\n"
        "Word objects save additional information such as:\n"
        f"index:\t\t{[i.index for i in words]}\n"
        f"sentence:\t{[i.sentence for i in words]}\n"
        f"POS tag:\t{[i.tag for i in words]}\n"
        f"Named Entity:\t{[i.ne for i in words]}"
    )
