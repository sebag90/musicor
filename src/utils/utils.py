from pathlib import Path
import os


def retrieve_files(dir_path):
    """
    collects all files in the given folder
    and return a list of Path-elements
    """
    file_list = []
    for path, _, files in os.walk(dir_path):
        if path == str(dir_path):
            for filename in files:
                file_list.append(Path(f"{path}/{filename}"))

    return file_list


def progress_bar(
        iteration, total, prefix='', suffix='', decimals=1,
        length=40, fill='#', miss=".", end="\r", stay=True,
        fixed_len=True):
    """
    Call in a loop to create terminal progress bar
    Parameters:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        miss        - Optional  : bar missing character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        stay        - Optional  : progress bar stays on terminal
        fiexed_len  - Optional  : length includes pre- and suffix
    """
    if fixed_len:
        bar_len = length - len(prefix) - len(suffix)
    else:
        bar_len = length

    percent = f"{100*(iteration/float(total)):.{decimals}f}"
    filled_length = int(bar_len * iteration // total)
    bar = f"{fill * filled_length}{miss * (bar_len - filled_length)}"
    to_print = f"\r{prefix} [{bar}] {percent}% {suffix}"
    print(to_print, end=end)

    # print new line on complete
    if iteration >= total:
        if stay:
            print()
        else:
            # clean line given lenght of lase print
            print(" "*len(to_print), end=end)


def save_results(results, output_file):
    """
    this function will create a tsv document
    where individual file evaluation is saved:
    name    precision   recall  F1
    """
    output_file = Path(output_file)

    # save results
    with open(output_file, "w", encoding="utf-8") as ofile:
        ofile.write("FILE\tPRECISION\tRECALL\tF1\n")
        for document, precision, recall, f1 in results:
            ofile.write(
                f"{document}\t"
                f"{round(precision, 5)}\t"
                f"{round(recall, 5)}\t"
                f"{round(f1, 5)}\n"
            )


def save_coref_clusters(coref_dict, ending, document, outputpath):
    """
    given a coreference dictionary this function saves
    it in a tsv file where each line is a new coreference chain
    and each mention of the chain is saved as a comma separated
    span. Chains with only one element are ignored
    ex.
        12,14   45,45
        34,45   65,68   78,79
    """
    # extract only document name
    filename = Path(str(document).split(os.sep)[-1])
    outputpath = Path(outputpath)

    # make sure output directory exists
    os.makedirs(outputpath, exist_ok=True)

    outputfile = Path(f"{outputpath}/{filename}.{ending}")

    # save coreference chains from dictionary
    with open(outputfile, "w", encoding="utf-8") as ofile:
        for key, value in coref_dict.items():
            if len(value) > 1:  # ignore singletons
                line = "\t".join((f"{i},{j}" for i, j in value))
                ofile.write(f"{line}\n")


def read_extracted(filepath):
    """
    given the path to a tsv file, this function will read the
    document and creates a coreference dictionary out of it
    """
    mapping = {}
    with open(Path(filepath), "r", encoding="utf-8") as infile:
        # i is a cluster
        for i, line in enumerate(infile):
            # separate spans
            line = line.strip().split("\t")

            # separate begin, end for each span
            line = [mention.split(",") for mention in line]

            # save coref cluster in mapping
            mapping[i] = [(int(begin), int(end)) for begin, end in line]

    return mapping
