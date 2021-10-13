"""
This class keeps track of mentions and clusters.
At the beginning each mention is mapped to
an unique cluster. The sieves can interact
with the ClusterContainer and merge coreference
clusters together. With the function get_pairs
the ClusterContainer calculates for each cluster
that has more than one mention the transitive
closure and returns a list of pairs of coreference
mentions. Each pair is a tuple of spans within the
document:
    ex. ((15, 18), (46, 52))
    --> token spans 15-18 and 46-52 are coreferential
"""


class ClusterContainer:

    def __init__(self, mentions, mapped=False):
        self.map = {}
        self.mentions = {}
        self.attributes = {}

        if mapped is False:
            # first mention has antecedent
            # cataphoric chains are not considered
            if len(mentions) > 0:
                mentions[0].antecedent = True

        for i, mention in enumerate(mentions):
            if mapped is False:
                # assign unique cluster to each mention
                mention.cluster = i

            # map mention to its span in self.mentions
            self.mentions[mention.span] = mention
            self.attributes[mention.cluster] = mention.attributes

    def __len__(self):
        return len(self.mentions)

    def __repr__(self):
        return str([str(i) for i in self.mentions.values()])

    def __getitem__(self, index):
        mentions = list(self.mentions.values())
        return mentions[index]

    def __iter__(self):
        return (i for i in self.mentions.values())

    def get_candidates(self, mention, document, pronoun=False):
        """
        given a mention, returns a  generator of candidates
        the candidates from the first sentence are in BFS-left to right
        order, those of the second sentences are:
            - BFS right to left if the mention is a pronoun
            - BFS left to right otherwise
        """
        this_sentence = mention.sentence

        # first get the candidates from this sentence
        # in BFS left-to-right order
        possible = [i for i in document.lr[this_sentence] if i < mention]

        # if not the first sentence, look for
        # candidates in previous sentence
        # in BFS right-to-left order
        previous_sentence = []
        if this_sentence != 0:
            prev = this_sentence - 1
            if pronoun:
                previous_sentence = [i for i in document.lr[prev]]
            else:
                previous_sentence = [i for i in document.rl[prev]]

        all_candidates = possible + previous_sentence

        for candidate in all_candidates:
            yield candidate

    def merge(self, this, that):
        """
        merge this mention into the cluster of that mention.
        this and that are mention objects. Attributes will
        also be updated.
        """
        # change cluster of this mention
        new_cluster = self.mentions[that.span].cluster
        self.mentions[this.span].cluster = new_cluster

        # merge attributes of mentions
        self.attributes[new_cluster] += this.attributes

        # this mention has antecedent
        self.mentions[this.span].antecedent = True

        # add pointer from that mention to this
        self.mentions[that.span].next = this.span

        # change cluster information of all
        # other mentions that are coreferential
        # with this mention
        next_node = self.mentions[this.span].next
        while next_node is not None:
            # update cluster information
            self.mentions[next_node].cluster = new_cluster

            # update cluster attributes
            to_add = self.mentions[next_node].attributes
            self.attributes[new_cluster] += to_add

            # go to next mention
            next_node = self.mentions[next_node].next

    def map_clusters(self):
        """
        after having applied all sieves to merge the clusters,
        this function creates a dictionary where clusters
        are saved as:
        {
            cluster_id : [list of Mention-objects],
            ...
        }
        """
        self.map = {}

        for mention in self.mentions.values():
            cluster = mention.cluster

            if cluster not in self.map:
                self.map[cluster] = []

            self.map[cluster].append(mention)

    def convert_mapping(self):
        self.map_clusters()
        result = {}

        for key, value in self.map.items():
            result[key] = [i.span for i in value]

        return result


if __name__ == "__main__":
    from mps.text.word import Word
    from mps.text.mention import Mention

    print("---DEMO: CLUSTER CONTAINER---")
    cl = ClusterContainer([
            Mention([Word("dutch", 1, 1, "NN", None)]),
            Mention([Word("holland", 2, 1, "NN", None)]),
            Mention([Word("netherlands", 3, 1, "NNS", None)]),
            Mention([Word("flemish", 13, 1, "NN", None)]),
            Mention([Word("belgium", 12, 1, "NN", None)])
        ])

    print(
        "The Cluster contains 5 Mentions\n"
        f"{cl}\n\n"
        "At the beginning, each mention is mapped"
        "to a new cluster:\n"
        f"{[i.cluster for i in cl]}\n\n"
        "After merging clusters, information such"
        "as cluster attributes get updated.\n"
        "Let's merge 'dutch', 'netherlands' and 'holland'"
        "in one cluster and 'flemish' and 'belgium' in another.",
        end=" "
    )
    cl.merge(cl[1], cl[0])
    cl.merge(cl[2], cl[1])
    cl.merge(cl[4], cl[3])

    print(
        "Let's take a look at the new clusters:\n"
        f"{[i.cluster for i in cl]}\n\n"
        "and not at the merged attributes of cluster 0:\n"
        f"{cl.attributes[0]}\n\n"
        "And finally we can convert create a mapping dictionary "
        "containing coreference information from the mentions:"
    )
    cl.map_clusters()
    converted = cl.convert_mapping()
    print(
        f"Mapping using Mention Objects:"
    )
    for cluster, mentions in cl.map.items():
        print(f"{cluster}: {mentions}")

    print(
        "\nsame mapping using spans:"
    )
    for cluster, mentions in converted.items():
        print(f"{cluster}: {mentions}")
