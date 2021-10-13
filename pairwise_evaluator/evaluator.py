"""
The evaluator class calculates precision, recall and
F1 score based on unordered predictions and golden
labels. For every call of the evaluate_document function
the evaluator saves the number of predictions, golden
labels and theirs intersection to calculate precision,
recall and F1 score on the entire data set
"""


class Evaluator:

    def __init__(self):
        self.dataset_found = 0
        self.dataset_gold = 0
        self.dataset_prediction = 0

    def reset(self):
        self.__init__()

    @staticmethod
    def __transitive_closure(mapping):
        """
        for each corefence cluster calculates the
        transitive closure of the elements. These
        are saved as tuples of indexes
        """
        pairs = []
        for coref_set in mapping.values():
            if len(coref_set) > 1:  # ignore singletons
                for i in range(len(coref_set)):
                    for j in range(i+1, len(coref_set)):

                        # save pair of spans
                        pair = (coref_set[i], coref_set[j])
                        pairs.append(pair)

        return pairs

    @staticmethod
    def __precision(found, prediction):
        if prediction == 0:
            return 0
        return found/prediction

    @staticmethod
    def __recall(found, gold):
        if gold == 0:
            return 0
        return found/gold

    @staticmethod
    def __f1_score(precision, recall):
        if precision + recall == 0:
            return 0
        return 2 * precision * recall / (precision + recall)

    def evaluate_document(self, preds_mapping, gold_mapping):
        """
        evaluates a single document by calculating:
            - precision
            - recall
            - f1
        """
        # create transitive closure
        prediction = self.__transitive_closure(preds_mapping)
        gold = self.__transitive_closure(gold_mapping)

        # create sets
        prediction = set(prediction)
        gold = set(gold)
        found = prediction.intersection(gold)

        # convert to integers
        prediction = len(prediction)
        gold = len(gold)
        found = len(found)

        # save for data set evaluation
        self.dataset_found += found
        self.dataset_gold += gold
        self.dataset_prediction += prediction

        # calculate precision, recall and f1 for document
        precision = self.__precision(found, prediction)
        recall = self.__recall(found, gold)
        f1 = self.__f1_score(precision, recall)

        return precision, recall, f1

    def evaluate_dataset(self):
        """
        calculates precision, recall and f1 for the entire
        data set using the numbers saved from evaluate_document
        calls
        """
        precision = self.__precision(
            self.dataset_found, self.dataset_prediction
        )

        recall = self.__recall(
            self.dataset_found, self.dataset_gold
        )

        f1 = self.__f1_score(precision, recall)

        return precision, recall, f1
