from src.main_functions.evaluation import evaluate
from src.main_functions.extraction import extract
from src.utils.cli import parse_arguments
from src.utils.errors import InvalidArgument


def main():
    args = parse_arguments()

    if args.subparser == "extract":
        extract(args)
    elif args.subparser == "evaluate":
        evaluate(args)
    else:
        raise InvalidArgument(
            "Selected argument not supported"
        )


if __name__ == "__main__":
    main()
