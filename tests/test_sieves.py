import unittest

from nltk.tree import Tree

from mps.text.word import Word
from mps.text.document import Document
from mps.text.cluster_container import ClusterContainer
from mps.sieves.exact_match_sieve import ExactMatch
from mps.sieves.precise_constructs_sieve import PreciseConstructs
from mps.sieves.pronoun_sieve import Pronoun


class Test(unittest.TestCase):

    def get_doc(self):
        """
        prepare a document for testing
        """

        doc = Document([], [], [], [], [], [])

        tree1 = Tree.fromstring(
            "(TOP (S (NP (NP Crew members) (VP injured (PP in "
            "(NP (NP the explosion) (PP on (NP the `` USS Cole ''))))))"
            " (VP are (VP coming (ADVP home) (NP the explosion))).))"
        )

        tree2 = Tree.fromstring(
            "(TOP (S (NP (NP Most) (PP are (NP (NP them)"
            " (VP hurt)))) , (VP are (VP being (VP reunited (PP  with"
            " (NP (NP family) (PP in (NP (NP Norfolk) , (NP Virginia)))))"
            " , (PP  before (S (VP moving (PRT on) (PP to (NP "
            "(NP a naval hospital) (PP for (NP anh)))))))))).))"
        )

        tree3 = Tree.fromstring(
            "(TOP (S (NP (NP Sailors) (PP (ADVP still) aboard "
            "(NP the `` USS Cole ''))) (VP paused (NP this morning)(PP for "
            "(NP  (NP a memorial service) (VP  honoring (NP "
            "(NP the 17 sailors) (SBAR (WHNP who) (S (VP died "
            "(PP in (NP the blast)))))))))).))"
        )

        doc.pos_tags = [
            'NNS', 'NNS', 'VBN', 'IN', 'DT', 'NN', 'IN', 'DT', '``',
            'NNP', 'NNP', "''", 'VBP', 'VBG', 'RB', 'NN', 'NN', '.',
            'JJS', 'IN', 'PRN', 'VBN', ',', 'VBP',
            'VBG', 'VBN', 'IN', 'NN', 'IN', 'NNP', ',', 'NNP',
            ',', 'IN', 'VBG', 'RP', 'IN', 'NNP', 'NNP', 'NNP',
            'IN', 'NNP', '.',
            'NNS', 'RB', 'IN', 'DT', '``', 'NNP', 'NNP', "''",
            'VBD', 'DT', 'NN', 'IN', 'DT', 'JJ', 'NN', 'VBG',
            'DT', 'CD', 'NNS', 'WP', 'VBD', 'IN', 'DT', 'NN', '.'
        ]

        doc.ner = [None for i in range(len(doc.pos_tags))]
        doc.ner[1] == "PERSON"

        # create sentences
        doc.tokens = tree1.leaves() + tree2.leaves() + tree3.leaves()
        sentence1 = slice(0, len(tree1.leaves()))
        sentence2 = slice(
            len(tree1.leaves()),
            len(tree1.leaves()) + len(tree2.leaves())
        )
        sentence3 = slice(
            len(tree1.leaves()) + len(tree2.leaves()),
            len(doc.tokens)
        )

        doc.sentences = [sentence1, sentence2, sentence3]

        start_position = 0
        for sen, t in enumerate([tree1, tree2, tree3]):
            # substitute leaves with Word objects to
            # keep track of the index of the word in the document
            leaves = t.treepositions("leaves")

            for i, leaf in enumerate(leaves):
                string = t[leaf]
                tag = doc.pos_tags[start_position + i]
                ner = doc.ner[start_position + i]
                mention = Word(string, start_position + i, sen, tag, ner)
                t[leaf] = mention

            start_position += len(t.leaves())

            doc.trees.append(t)

        doc.extract_nps()
        mentions = doc.nps
        cl = ClusterContainer(mentions)

        return doc, cl

    def test_exact_match_sieve(self):
        """
        test the exact match sieve
        """
        doc, cl = self.get_doc()
        sieve = ExactMatch()
        cl = sieve(doc, cl)

        # mention 2 and 5 should be coreferential
        # [the explosion] ... [the explosion]
        self.assertEqual(cl[2].cluster, cl[5].cluster)

    def test_precise_construct_sieve_appositive(self):
        """
        test the precise construc sieve:
        appositive construct
        """
        doc, cl = self.get_doc()
        sieve = PreciseConstructs()
        cl = sieve(doc, cl)

        # mention 13 and 14 should be coreferential
        # [Norfolk], [Virginia], ...
        self.assertEqual(cl[13].cluster, cl[14].cluster)

    def test_precise_construct_sieve_head(self):
        """
        test the precise construc sieve:
        head of construct
        """
        doc, cl = self.get_doc()
        sieve = PreciseConstructs()
        cl = sieve(doc, cl)

        # 0 and 1 should be coreferential
        # [[Crew members] injured in the explosion on the `` USS Cole '']
        self.assertEqual(cl[0].cluster, cl[1].cluster)

    def test_precise_construct_sieve_acronym(self):
        """
        test the precise construc sieve:
        acronym
        """
        doc, cl = self.get_doc()
        sieve = PreciseConstructs()
        cl = sieve(doc, cl)

        # 15 and 17 should be coreferential
        # [a naval hospital] ... [anh]
        self.assertEqual(cl[15].cluster, cl[17].cluster)

    def test_precise_construct_sieve_predicative(self):
        """
        test the precise construc sieve:
        predicative
        """
        doc, cl = self.get_doc()
        sieve = PreciseConstructs()
        cl = sieve(doc, cl)

        # 6 and 8 should be coreferential
        # [Most] are [them]
        self.assertEqual(cl[8].cluster, cl[6].cluster)

    def test_pronoun_sieve(self):
        """
        test pronoun sieve
        """
        doc, cl = self.get_doc()
        sieve = Pronoun()
        cl = sieve(doc, cl)

        # 1 and 8 should be coreferential
        # [Crew members injured in the explosion
        # on the `` USS Cole ''] ... [them]
        self.assertEqual(cl[1].cluster, cl[8].cluster)
