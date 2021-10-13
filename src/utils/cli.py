import argparse
import configparser
import os


def parse_arguments():
    """
    argument parser for the main file
    """
    parser = argparse.ArgumentParser(
        prog="musicor",
        description=(
            "MuSiCoR: "
            "Multi-Sieve Coreference Resolutor"
        )
    )

    # add subparsers (2)
    subparsers = parser.add_subparsers(dest="subparser")

    # extraction
    parser_extract = subparsers.add_parser(
        "extract", help="extract coreference information"
    )

    parser_extract.add_argument(
        "path", metavar="PATH", action="store",
        help="Path to the configuration file"
    )

    parser_extract.add_argument(
        "-s", "--single", action="store_true",
        help="disable concurrency"
    )

    # evaluation
    parser_evaluate = subparsers.add_parser(
        "evaluate",
        help=(
            "evaluate the performance of "
            "the extraction against a golden standard"
        )
    )

    parser_evaluate.add_argument(
        "path", metavar="PATH", action="store",
        help=(
            "Path to the folder containing the "
            "extracted files"
        )
    )

    parser_evaluate.add_argument(
        "-v", "--verbose", action="store_true",
        help=(
            "Additionally saves a log file with "
            "precision, recall and f1 score for "
            "each single file"
        )
    )

    # check that arguments are safe
    args = parser.parse_args()
    subparser = args.subparser

    if subparser == "extract":
        # make sure config file exists
        if not os.path.exists(args.path):
            raise FileNotFoundError("File not found")

        config = configparser.ConfigParser()
        config.read(args.path)

        # make sure path to input directory exists
        if not os.path.exists(config["PATH"]["input"]):
            raise FileNotFoundError("Input directory not found")

        # make sure input path is a directory
        if not os.path.isdir(config["PATH"]["input"]):
            raise NotADirectoryError(config["PATH"]["input"])

    elif subparser == "evaluate":
        # make sure directory exists
        if not os.path.exists(args.path):
            raise NotADirectoryError(
                "Invalid input directory"
            )

        # make sure directory is not empty
        if not os.listdir(args.path):
            raise FileNotFoundError(
                "Empty input directory"
            )

    return args
