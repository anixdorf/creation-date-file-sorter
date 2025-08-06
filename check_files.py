import argparse
from lib.operations import check_files


def main():
    parser = argparse.ArgumentParser(
        description="Checks files according to a generated copy list."
    )
    parser.add_argument(
        "--copy-list", help="Path to the copy list CSV file", required=True
    )
    args = parser.parse_args()

    check_files(args.copy_list)


if __name__ == "__main__":
    main()
