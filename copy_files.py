import argparse
from lib.operations import copy_files


def main():
    parser = argparse.ArgumentParser(
        description="Copies files according to a generated copy list."
    )
    parser.add_argument(
        "--copy-list", help="Path to the copy list CSV file", required=True
    )
    args = parser.parse_args()

    copy_files(args.copy_list)


if __name__ == "__main__":
    main()
