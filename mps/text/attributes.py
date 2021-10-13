"""
This class represents linguistic attributes
of mentions:
    - number
    - genus
    - person
    - animacy
"""


class Attributes:

    def __init__(self, mention=None):
        self.number = set()
        self.genus = set()
        self.person = set()
        self.animacy = set()
        if mention is not None:
            self.calculate_number(mention)
            self.calculate_animacy(mention)

    def __eq__(self, other):
        if ((self.number == other.number) and
                (self.genus == other.genus) and
                (self.person == other.person) and
                (self.animacy == other.animacy)):
            return True

        return False

    def __repr__(self):
        return (
            f"num: {self.number}, "
            f"gen: {self.genus}, "
            f"per: {self.person}, "
            f"ani: {self.animacy}"
        )

    def calculate_number(self, mention):
        """
        given a list of words, this function
        will try to extract the number of
        the NP:
            - NP is a pronoun: the number is
                based on a list
            - NP is complex: the head of the NP
                will be identified (naive assumption:
                the first noun in the NP is the head)
                ant the number will be based on the
                tag of that noun
        """
        pronouns = {
            "I": {"singular"},
            "me": {"singular"},
            "you": {"singular", "plural"},
            "he": {"singular"},
            "him": {"singular"},
            "she": {"singular"},
            "her": {"singular"},
            "we": {"plural"},
            "us": {"plural"},
            "they": {"plural"},
            "them": {"plural"},
        }

        if len(mention.words) == 1:
            symbol = mention.words[0].symbol.lower()
            if symbol in pronouns:
                self.number = pronouns[symbol]

                if symbol in {"I", "me", "we", "us"}:
                    self.person.add(1)
                elif symbol in {"you"}:
                    self.person.add(2)
                elif symbol in {"he", "him", "she", "her", "they", "them"}:
                    self.person.add(3)

        head = mention.head
        if head:
            if head.tag[-1] == "S":
                if not self.number:
                    self.number = set(["plural"])
            else:
                if not self.number:
                    self.number = set(["singular"])

    def calculate_animacy(self, mention):
        """
        using NE annotation this function decides
        whether the mention animate is or not
        """
        head = mention.head
        if head:
            if head.ne == "PERSON":
                self.animacy.add(True)
            else:
                self.animacy.add(False)

    @staticmethod
    def compatible(this, other, number=False):
        """
        helper function for the method is_subset to
        check whether 2 attributes are compatible.
        Since a lot of NPs only have number as an
        attribute, the other ones will not be enforced
        (will evaluate true) if the other set is empty.
        This rule does not apply to the number (first
        if-else block)
        """

        if number is False:
            if len(other) == 0:
                return True
        else:
            if len(this) == len(other) == 0:
                return False

        if len(this) > 0 and this.issubset(other):
            return True
        elif len(other) != 0 and this.issubset(other):
            return True
        else:
            return False

    def is_subset(self, other):
        """
        this function decides whether this attribute instance
        is a subset of another attribute instance by
        comparing the 4 attribute sets:
            - number
            - genus
            - person
            - animacy
        """
        # if all are empty, false
        if (all(len(i) == 0 for i in self.__dict__.values()) and
                all(len(i) == 0 for i in other.__dict__.values())):
            return False

        n = self.compatible(self.number, other.number, True)
        g = self.compatible(self.genus, other.genus)
        p = self.compatible(self.person, other.person)
        a = self.compatible(self.animacy, other.animacy)

        return (n and g and p and a)

    def __add__(self, other):
        """
        join 2 attributes object
        """
        new = Attributes()

        new.number = self.number.union(other.number)
        new.get_head = self.genus.union(other.genus)
        new.person = self.person.union(other.person)
        new.animacy = self.animacy.union(other.animacy)

        return new


if __name__ == "__main__":
    from mps.text.word import Word
    from mps.text.mention import Mention

    print("---DEMO: ATTRIBUTES---")
    m1 = Mention([
        Word("the", 0, 0, "ART", None),
        Word("captain", 1, 0, "NN", "PERSON")
    ])

    m2 = Mention([
        Word("the", 0, 0, "ART", None),
        Word("ship", 1, 0, "NNS", None),
        Word("in", 2, 0, "PRP", None),
        Word("Jakarta", 3, 0, "PNN", None)
    ])

    m3 = Mention([
        Word("the", 10, 2, "ART", None),
        Word("ship", 11, 2, "NN", "PERSON")
    ])

    print(
        "Mentions will calculate automatically"
        "attributes upon being created:\n"
        f"{m1}:\t{m1.attributes}\n\n"
        "Attributes can also decide if they are compatible"
        "with each other:\n"
        f"attributes 1: {m1.attributes}\n"
        f"attributes 2: {m2.attributes}\n"
        f"compatible: {m1.attributes.is_subset(m2.attributes)}\n\n"
        "Finally Attributes can be merged together:\n"
        f"attributes 1: {m1.attributes}\n"
        f"attributes 2: {m2.attributes}\n"
        f"1 + 2 =  {m1.attributes + m2.attributes}"
    )
