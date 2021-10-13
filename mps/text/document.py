"""
The document class represents a document
that can parse a conll file and save
following information:
    - sentence boundaries
    - tokens
    - pos tags
    - trees (nltk.Tree)
    - coreference sets (for evaluation)
"""

from nltk.tree import Tree

from mps.text.cluster_container import ClusterContainer
from mps.text.mention import Mention
from mps.text.word import Word
from mps.utils.errors import DocumentNotParsed
from mps.utils.utils import levelorder


class Document:

    def __init__(self, sentences, tokens, pos_tags, ner, trees, coref):
        # TODO: add check sentence==trees, tokens==pos_tags
        self.sentences = sentences
        self.tokens = tokens
        self.pos_tags = pos_tags
        self.ner = ner
        self.trees = trees
        self.coref = coref
        self.nps = []
        self.lr = []
        self.rl = []

    def process(self):
        self.convert_trees()
        self.extract_nps()
        self.convert_coref()

    def convert_trees(self):
        """
        convert trees from string to nltk.Tree
        substitute leaves of syntax trees with Word objects to
        keep track of the index of the word in the document
        """
        tok_counter = 0
        for t, string_tree in enumerate(self.trees):

            # create tree from string
            tree = Tree.fromstring(string_tree)
            leaves_position = tree.treepositions("leaves")

            for leaf in leaves_position:
                string = self.tokens[tok_counter]
                tag = self.pos_tags[tok_counter]
                ner = self.ner[tok_counter]

                # create a word and append it to the tree
                mention = Word(
                    string, tok_counter, t, tag, ner
                    )
                tree[leaf] = mention
                tok_counter += 1

            self.trees[t] = tree

    def extract_nps(self):
        """
        Extracts NPs from the trees and save them as
        Mention-objects in self.nps. In this step,
        each tree is traversed in BFS order left to right
        and right to left and right to lefts. NPs are
        then saved to avoid calling BFS multiple times on
        the same tree
        """
        if not self.trees:
            raise DocumentNotParsed(
                "Missing Trees"
            )

        for tree in self.trees:
            # traverse tree in left_to_right BFS fashion
            nps = levelorder(tree, False)
            mentions = []
            for np in nps:
                if np.label() == "NP":
                    mention = Mention(np.leaves())
                    mention.tree = np
                    mentions.append(mention)

            # add mentions to total mentions and RtL list
            self.nps += mentions
            self.lr.append(mentions)

            # traverse same tree in right-to-left BFS fashion
            nps = levelorder(tree, True)
            mentions = []
            for np in nps:
                if np.label() == "NP":
                    mention = Mention(np.leaves())
                    mention.tree = np
                    mentions.append(mention)
            self.rl.append(mentions)

        self.nps.sort()

    def convert_coref(self):
        """
        convert list of Word-indexes into Mentions
        and save the mentions and their mapping
        into a ClusterContainer-object for evaluation
        """
        mentions = []

        # convert list of indeces into Mentions
        for cluster, word_lists in self.coref.items():
            for i, w_list in enumerate(word_lists):
                words = []

                # convert indeces into Words
                for word_index in w_list:
                    token = self.tokens[word_index]
                    tag = self.pos_tags[word_index]
                    ner = self.ner[word_index]
                    sentence = 0
                    while word_index > self.sentences[sentence].stop - 1:
                        sentence += 1
                    words.append(Word(token, word_index, sentence, tag, ner))

                # create a mention
                this_mention = Mention(words)
                this_mention.cluster = int(cluster)
                mentions.append(this_mention)

        # sort mentions
        mentions.sort()

        # create Cluster-object
        clusters = ClusterContainer(mentions, mapped=True)

        # save cluster object
        self.coref = clusters

    @property
    def text(self):
        return " ".join(self.tokens)
