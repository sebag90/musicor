from abc import ABC, abstractmethod


class Sieve(ABC):

    def __call__(self, document, clusters):
        processed = self.process(document, clusters)
        return processed

    @abstractmethod
    def process(self, document, clusters):
        # do something with the document and clusters
        # only return clusters
        return clusters

    def prune(self, mention):
        """
        pruning function to filter out mentions
        that starts with an indefinite pronoun
        or an indefinite article
        """
        to_exclude = {
            "a", "an", "anybody",
            "everybody", "nobody"
            "somebody", "anyone",
            "everyone", "someone",
            "anything", "everything",
            "nothing", "something"
        }
        first_word = mention.words[0].symbol.lower()
        if first_word in to_exclude:
            return True
        return False
