import configparser
import multiprocessing as mp

from datareader.conll_data_reader import ConllParser
from mps.multi_pass_sieve import MultiPassSieve
from mps.text.document import Document
from src.utils.utils import progress_bar, save_coref_clusters, retrieve_files


class Extractor:
    """
    this class manages the extraction function of MuSiCoR.
    it can extract coreference information working
    either in parallel or on a single thread
    """
    def __init__(self, outputpath, reader, mps):
        self.outputpath = outputpath
        self.reader = reader
        self.mps = mps

    @staticmethod
    def split_lists(list, n):
        """
        divide a list in n lists
        with equal number of elements
        """
        for i in range(0, n):
            yield list[i::n]

    def single(self, documents, verbose=False):
        """
        main processing function to extract coreference
        information from a document. This functions
        takes a list of paths to the documents as argument.
        with the verbose option, a progress bar will be
        printed at the end of each file
        """
        # process documents
        for i, document in enumerate(documents):
            data = self.reader(document)
            doc = Document(*data)
            doc.process()

            # extract coreference information with MPS
            clusters = self.mps(doc)

            # calculate cluster mapping
            preds = clusters.convert_mapping()
            gold = doc.coref.convert_mapping()

            # save predictions and goldens
            save_coref_clusters(preds, "preds", document, self.outputpath)
            save_coref_clusters(gold, "gold", document, self.outputpath)
            if verbose:
                progress_bar(
                    i+1, len(documents),
                    prefix=f"Extracting: {i+1}/{len(documents)}",
                    length=50
                )

    def multi(self, documents):
        """
        divides input in lists of equal size and distribute
        it among multiple threads to process more files
        at the same time
        """
        # create sublists for pool
        sublists = self.split_lists(documents, len(documents))

        with mp.Pool() as pool:
            for i, _ in enumerate(pool.imap(self.single, sublists)):
                progress_bar(
                    i+1, len(documents),
                    prefix=f"Extracting: {i+1}/{len(documents)}",
                    length=50
                )


def extract(args):
    """
    main function for the extraction
    """
    # extract arguments
    config = configparser.ConfigParser()
    config.read(args.path)
    inputpath = config["PATH"]["input"]
    outputpath = config["PATH"]["output"]
    sieves = [i.strip() for i in config["SIEVES"]["sieves"].split(",")]

    # retrieve documents
    documents = retrieve_files(inputpath)

    # instantiate MPS and extractor
    reader = ConllParser()
    mps = MultiPassSieve(sieves)
    ex = Extractor(outputpath, reader, mps)

    # extract
    if args.single:
        ex.single(documents, verbose=True)
    else:
        mp.set_start_method("spawn")
        ex.multi(documents)
