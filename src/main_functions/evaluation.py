import os
from pathlib import Path
import re

from pairwise_evaluator.evaluator import Evaluator
from src.utils.utils import (
    progress_bar,
    read_extracted,
    retrieve_files,
    save_results
)


def evaluate(args):
    """
    main function for the evaluation
    """
    evaluator = Evaluator()
    results = []
    inputpath = Path(args.path)
    documents = retrieve_files(inputpath)

    # collect file names
    pattern = re.compile(r".+(?=\.\w+$)")
    doc_names = set()
    for document in documents:
        # remove ending of files (.preds and .gold)
        name = re.match(pattern, str(document)).group()
        doc_names.add(name)

    for i, document in enumerate(doc_names):
        # read files
        preds = read_extracted(f"{document}.preds")
        gold = read_extracted(f"{document}.gold")

        # evaluate pairs
        precision, recall, f1 = evaluator.evaluate_document(preds, gold)

        # save docname and values for log
        doc_name = document.split(os.sep)[-1]
        results.append((doc_name, precision, recall, f1))
        progress_bar(
            i+1, len(doc_names),
            prefix=f"Evaluating: {i+1}/{len(doc_names)}",
            length=50
        )

    if args.verbose:
        save_results(results, "evaluation.log")

    precision, recall, f1 = evaluator.evaluate_dataset()

    print(
        f"Data set Evaluation:\n"
        f"Precision:\t{round(precision, 5):.5f}\n"
        f"Recall: \t{round(recall, 5):.5f}\n"
        f"F1 score:\t{round(f1, 5):.5f}"
    )
