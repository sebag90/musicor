import unittest

from mps.text.mention import Mention
from mps.text.word import Word


class Test(unittest.TestCase):

    word1 = Word("supercalifragilisticexpialidocious", 1, 1, "NNS", None)
    word2 = Word("supercalifragilisticexpialidocious", 2, 1, "NN", None)
    word3 = Word("Supercalifragilisticexpialidocious", 1, 1, "NN", None)

    mention1 = Mention([word1, word2])
    mention2 = Mention([word2, word2])
    mention3 = Mention([word1, word2])

    def test_equal_words(self):
        to_test = [
            self.word1 == self.word2,
            self.word1 == self.word3,
            self.word1.same_surface(self.word2),
            self.word1.same_surface(self.word3)
        ]

        gold = [
            False,
            False,
            True,
            True
        ]

        self.assertEqual(to_test, gold)

    def test_equal_mentions(self):
        to_test = [
            self.mention1 == self.mention2,
            self.mention1 == self.mention3,
            self.mention2.same_surface(self.mention1)
        ]

        gold = [
            False,
            True,
            True
        ]

        self.assertEqual(to_test, gold)

    def test_equal_attributes(self):
        to_test = [
            self.mention1.attributes == self.mention3.attributes,
            self.mention2.attributes == self.mention3.attributes,
        ]

        gold = [
            True,
            False
        ]

        self.assertEqual(to_test, gold)
