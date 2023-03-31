import argparse
import hashlib
import logging
from multiprocessing import Pool
from pathlib import Path

from tqdm import tqdm

from lib.dateparser.dateparser import parse_date
from lib.get_file_creation_date.get_file_creation_date import get_file_creation_date
from lib.scantree import scantree
from lib.setup_logging import setup_logging


def _read_existing_entries(copy_list_filename, logger):
    logger.info(f"Reading existing list {copy_list_filename}")
    existing_creation_dates = {}
    if Path(copy_list_filename).exists():
        with open(copy_list_filename, "rt", encoding="utf-8") as f:
            for i, line in enumerate(f.readlines()):
                line = line.strip()
                if i > 1 and not line.startswith("#"):
                    source_file_path, date, field, _ = line.split(";")
                    existing_creation_dates[source_file_path] = (field, parse_date(date))
    logger.info(f"Found {len(existing_creation_dates)} existing entries")
    return existing_creation_dates


def _get_destination_path(path, create_datetime, destination):
    year = create_datetime.strftime("%Y")
    month = create_datetime.strftime("%m")
    return str(Path(destination) / year / month / Path(path).name)


def _create_copy_list(source, destination, copy_list_id):
    setup_logging(f"create_copy_list_{copy_list_id}")
    logger = logging.getLogger(__name__)

    copy_list_filename = f"copy-list-{copy_list_id}.csv"
    existing_creation_dates = _read_existing_entries(copy_list_filename, logger)

    logger.info("Scanning source directory: %s", source)
    files = []
    for entry in scantree(source):
        if entry.is_file():
            files.append(entry.path)

    logger.info("Start processing %d files", len(files))
    with open(copy_list_filename, "wt", encoding="utf-8") as f:
        f.write(f"# COPY LIST {source} -> {destination}\n")
        f.write(f"source;date;field;destination\n")
        for file_path in tqdm(files):
            if file_path in existing_creation_dates:
                method, creation_date = existing_creation_dates[file_path]
            else:
                result = get_file_creation_date(file_path)
                if result:
                    method, creation_date = result.method, result.creation_date
                else:
                    print(f"Could not find creation date for {file_path}!")
                    assert(False)
                    continue
            destination_path = _get_destination_path(file_path, creation_date, destination)
            f.write(f"{file_path};{creation_date};{method};{destination_path}\n")
        f.write(f"# END OF FILE\n")
    logger.info("Done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="source directory", required=True, nargs="+", action="extend")
    parser.add_argument("--destination", help="destination directory", required=True)
    args = parser.parse_args()

    with Pool() as p:
        work_list = [
            (
                source,
                args.destination,
                hashlib.sha256(bytes(source, "utf-8")).hexdigest()[:8]
            )
            for i, source in enumerate(args.source)]
        p.starmap(_create_copy_list, work_list)


if __name__ == "__main__":
    main()
