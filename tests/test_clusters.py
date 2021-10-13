import unittest

from mps.text.mention import Mention
from mps.text.word import Word
from mps.text.cluster_container import ClusterContainer


class Test(unittest.TestCase):

    def get_cluster(self):
        """
        prepare a cluster with mentions for the tests

        ---

        G: What is Holland?
        J: What do you mean what is it? It's a country
           right next to Belgium
        G: Noo, that's the Netherlands
        J: Holland is the Netherlands
        G: Then who are the Dutch!?
        """

        cl = ClusterContainer([
            Mention([Word("dutch", 1, 1, "NN", None)]),
            Mention([Word("holland", 2, 1, "NN", None)]),
            Mention([Word("netherlands", 3, 1, "NNS", None)]),
            Mention([Word("flemish", 13, 1, "NN", None)]),
            Mention([Word("belgium", 12, 1, "NNS", None)])
        ])

        return cl

    def test_create_chains(self):
        """
        test clusters after merging clusters
        """
        cl = self.get_cluster()
        # dutch - holland - netherlands
        # these should get cluster 0

        cl.merge(cl[1], cl[0])
        cl.merge(cl[2], cl[1])

        # flemish - belgium
        # should get cluster 3 (of word flemish)

        cl.merge(cl[4], cl[3])

        gold = [0, 0, 0, 3, 3]
        to_test = [i.cluster for i in cl]

        self.assertEqual(to_test, gold)

    def test_merge_chains(self):
        """
        check clusters after merging two
        clusters with more than one element
        """
        cl = self.get_cluster()
        # dutch - holland - netherlands
        # these should get cluster 0
        cl.merge(cl[1], cl[0])
        cl.merge(cl[2], cl[1])

        # flemish - belgium
        # should get cluster 3 (of word flemish)
        cl.merge(cl[4], cl[3])

        # link flemish and netherlands
        # all into cluster 0
        cl.merge(cl[3], cl[2])

        gold = [0, 0, 0, 0, 0]
        to_test = [i.cluster for i in cl]

        self.assertEqual(to_test, gold)

    def test_next_chains(self):
        """
        check that the next attribute gets
        changed after merging clusters
        """
        cl = self.get_cluster()
        # dutch - holland - netherlands
        cl.merge(cl[1], cl[0])
        cl.merge(cl[2], cl[1])

        # flemish - belgium
        # should get cluster 3 (of word flemish)
        cl.merge(cl[4], cl[3])

        gold = [(2, 2), (3, 3), None, (12, 12), None]
        to_test = [i.next for i in cl]

        self.assertEqual(to_test, gold)

    def test_antecedent_chains(self):
        """
        check that the antecedent attribute gets
        changed after merging clusters
        """
        cl = self.get_cluster()
        # dutch - holland - netherlands
        cl.merge(cl[1], cl[0])
        cl.merge(cl[2], cl[1])

        # flemish - belgium
        # should get cluster 3 (of word flemish)
        cl.merge(cl[4], cl[3])

        gold = [True, True, True, False, True]
        to_test = [i.antecedent for i in cl]

        self.assertEqual(to_test, gold)

    def test_attributes_merging(self):
        """
        check that cluster attributes get
        updated after merging clusters
        """
        cl = self.get_cluster()
        # dutch - holland - netherlands
        cl.merge(cl[1], cl[0])
        cl.merge(cl[2], cl[1])

        # flemish - belgium
        # should get cluster 3 (of word flemish)
        cl.merge(cl[4], cl[3])

        gold = cl.attributes[0]
        to_test = cl[0].attributes + cl[1].attributes + cl[2].attributes
        self.assertEqual(to_test, gold)
