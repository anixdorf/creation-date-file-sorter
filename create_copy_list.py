import argparse
from lib.operations import generate_copy_list


def main():
    parser = argparse.ArgumentParser(
        description="Generate a list of files to be copied based on creation dates."
    )
    parser.add_argument(
        "--source",
        help="One or more source directories",
        required=True,
        nargs="+",
        action="extend",
    )
    parser.add_argument(
        "--destination", help="The root destination directory", required=True
    )
    args = parser.parse_args()

    generate_copy_list(args.source, args.destination)


if __name__ == "__main__":
    main()
