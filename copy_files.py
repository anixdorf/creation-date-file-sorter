import shutil
import logging
import hashlib
import argparse
from pathlib import Path

from lib.setup_logging import setup_logging


def _get_hash(file_path: str) -> str:
    with open(file_path, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy-list", help="copy list", default="copy-list.csv")
    args = parser.parse_args()

    setup_logging(f"copy_files")
    logger = logging.getLogger(__name__)

    logger.info(f"Reading copy list")
    entries =  [] 
    with open(args.copy_list, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f.readlines()):
            line = line.strip()
            if i > 1 and not line.startswith("#"):
                source, date, field, destination = line.split(";")
                entries.append((source, date, field, destination))

    destinations = set()
    for source, date, field, destination in entries:
        destinations.add(destination)
    logger.info(f"Duplicate destinations: {len(entries) - len(destinations)}")
    
    logger.info(f"Copying {len(entries)} files")
    for source, date, field, destination in entries:
        logging.info(f"Copying {source} to {destination}")
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        i = 1
        while Path(destination).is_file():
            source_hash = _get_hash(source)
            destination_hash = _get_hash(destination)
            if source_hash != destination_hash:
                destination = destination.parent / (destination.stem + f"_dup_{i}" + destination.suffix)
            else:
                break
        shutil.copy2(source, destination)
    logger.info("Done")



if __name__ == "__main__":
    main()
