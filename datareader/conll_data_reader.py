"""
This data reader is designed to read the CONLL input
files from the onto notes data set.
The data reader will also check if the input file
has the required amount of columns needed for the
extraction. The existence of the last column (coreference
information) is not enforced. If it doesn't exists the
regex expression will simply not find any coreference information
"""

from pathlib import Path
import re

from datareader.errors import InvalidInputFile


class ConllParser:

    def __init__(self):
        self.sentences = []
        self.tokens = []
        self.pos_tags = []
        self.ner = []
        self.trees = []
        self.coref = {}
        self.temp = {}
        self.ner_open = False
        self.tok_counter = 0

    def __call__(self, path):
        self.__parse_connl(path)
        to_return = (
            self.sentences,
            self.tokens,
            self.pos_tags,
            self.ner,
            self.trees,
            self.coref
        )

        # reset for next file
        self.__init__()

        return to_return

    def __extract_ne(self, ner):
        """
        extract information from the named entity column
        """
        # extract named entity
        opening_ner = re.match(r"(\()(\w+)", ner)

        # start collecting ner tags
        if opening_ner is not None:
            ner_tag = opening_ner.group(2)
            self.ner.append(ner_tag)
            self.ner_open = True

        # if ner is open, copy last ner tag
        elif self.ner_open is True:
            last_element = self.ner[-1]
            self.ner.append(last_element)

        else:
            self.ner.append(None)

        # check for closing ner
        closing_ner = re.match(r"(.+)\)", ner)
        if closing_ner:
            self.ner_open = False

    def __extract_golden_coref(self, coref):
        """
        extract golden coreference clusters
        """
        # check if coreference sets are being opened or closed
        opening_sets = re.findall(r"\((\d+)", coref)
        closing_sets = re.findall(r"(\d+)\)", coref)

        # start a new coreference cluster for each opening set
        for oset in opening_sets:
            if oset not in self.temp:
                self.temp[oset] = []

            # use a "stack" to keep track of nested mentions
            self.temp[oset].append([])

        # add current token to all opened coreference clusters
        for key in self.temp:
            if len(self.temp[key]) > 0:
                for i in range(len(self.temp[key])):
                    self.temp[key][i].append(self.tok_counter)

        # save and close all closing coreference clusters
        for cset in closing_sets:
            if cset not in self.coref:
                self.coref[cset] = []
            self.coref[cset].append(self.temp[cset][-1])
            del self.temp[cset][-1]

    def __parse_connl(self, path):
        """
        read line by line a document and save:
            - sentences (list of slices)
            - tokens (list of strings)
            - pos tags (list of strings)
            - trees (list of strings)
            - golden coreference information (dictionary):
                {
                    "clusterID" : [[index_word_1, index_word_2], ...]
                }
        """

        with open(Path(path), "r", encoding="utf-8") as infile:
            last_sent = 0
            this_tree = ""

            for line in infile:
                line = line.strip()

                if line == "":
                    # empty line --> new sentence
                    # update sentence boundaries
                    self.sentences.append(slice(last_sent, self.tok_counter))
                    last_sent = self.tok_counter

                    # save tree
                    self.trees.append(this_tree)
                    this_tree = ""

                elif line[0] == "#":
                    # begin and end of document
                    # do nothing
                    pass

                else:
                    # increment sentence counter
                    # and clean line
                    line = line.split()

                    # make sure the file has at least 10 columns
                    if not len(line) > 9:
                        raise InvalidInputFile(
                            "Input file is not in recognized CONLL format:\n"
                            f"{path}"
                        )

                    # extract information and save it
                    token = line[3]
                    tag = line[4]
                    tree = line[5]
                    ner = line[10]
                    coref = line[-1]

                    # extract NE and golden coref
                    self.__extract_ne(ner)
                    self.__extract_golden_coref(coref)

                    self.tokens.append(token)
                    self.pos_tags.append(tag)

                    # create string for tree
                    tree = tree.replace("*", f" {token}")
                    this_tree += tree
                    self.tok_counter += 1
