import hashlib
import logging
import shutil
from pathlib import Path
from tqdm import tqdm
import glob

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
                    source_file_path, date, provider, provider_info, _ = line.split(";")
                    existing_creation_dates[source_file_path] = (
                        parse_date(date),
                        provider,
                        provider_info,
                    )
    logger.info(f"Found {len(existing_creation_dates)} existing entries")
    return existing_creation_dates


def _get_destination_path(path, create_datetime, destination):
    year = create_datetime.strftime("%Y")
    month = create_datetime.strftime("%m")
    return str(Path(destination) / year / month / Path(path).name)


#
# Step 1: Generate
#


def generate_copy_list(source_dirs: list[str], destination_dir: str):
    """
    Scans source directories, extracts creation dates, and generates a copy list for each source.
    """
    logger = logging.getLogger(__name__)

    for source in source_dirs:
        list_id = hashlib.sha256(bytes(source, "utf-8")).hexdigest()[:8]
        copy_list_filename = f"copy-list-{list_id}.csv"

        setup_logging(f"create_copy_list_{list_id}", stdout_level=logging.FATAL)
        logger.info(f"Processing source: {source}")

        existing_creation_dates = _read_existing_entries(copy_list_filename, logger)

        logger.info("Scanning source directory: %s", source)
        files = [entry.path for entry in scantree(source) if entry.is_file()]

        logger.info("Start processing %d files", len(files))
        with open(copy_list_filename, "wt", encoding="utf-8") as f:
            f.write(f"# COPY LIST {source} -> {destination_dir}\n")
            f.write(f"source;date;provider;provider_info;destination\n")

            for file_path in tqdm(files, desc=f"Analyzing {Path(source).name}"):
                logger.info(f"Processing {file_path}")
                if file_path in existing_creation_dates:
                    creation_date, provider, provider_info = existing_creation_dates[
                        file_path
                    ]
                else:
                    result = get_file_creation_date(file_path)
                    if result:
                        creation_date, provider, provider_info = (
                            result.creation_date,
                            result.provider,
                            result.provider_info,
                        )
                    else:
                        logger.error(f"Could not find creation date for {file_path}!")
                        continue

                destination_path = _get_destination_path(
                    file_path, creation_date, destination_dir
                )
                f.write(
                    f"{file_path};{creation_date};{provider or ''};{provider_info or ''};{destination_path}\n"
                )

            f.write(f"# END OF FILE\n")
        logger.info(f"Generated copy list: {copy_list_filename}")


def _get_hash(file_path: str) -> str:
    with open(file_path, "rb", buffering=0) as f:
        return hashlib.file_digest(f, "blake2b").hexdigest()


#
# Step 2: Copy
#
def copy_files(copy_list_path: str):
    """
    Reads a copy list and executes the file copy operations.
    """
    setup_logging(f"copy_files")
    logger = logging.getLogger(__name__)

    logger.info(f"Reading copy list from {copy_list_path}")
    entries = []
    with open(copy_list_path, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if i > 1 and not line.startswith("#"):
                source, date, provider, provider_info, destination = line.split(";")
                entries.append((source, destination))

    logger.info(f"Copying {len(entries)} files")
    created_dirs = set()
    for source, destination in tqdm(entries, desc="Copying files"):
        original_destination_path = Path(destination)
        current_destination_path = original_destination_path

        dest_dir = current_destination_path.parent
        if dest_dir not in created_dirs:
            dest_dir.mkdir(parents=True, exist_ok=True)
            created_dirs.add(dest_dir)

        source_hash = _get_hash(source)
        i = 1
        while current_destination_path.is_file():
            destination_hash = _get_hash(current_destination_path)
            if source_hash != destination_hash:
                current_destination_path = original_destination_path.parent / (
                    original_destination_path.stem
                    + f"_dup_{i}"
                    + original_destination_path.suffix
                )
                i += 1
            else:
                logger.debug(f"Skipping identical file: {source}")
                break
        else:
            shutil.copy2(source, current_destination_path)

    logger.info("Done copying files.")


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"


#
# Step 3: Check
#
def check_files(copy_list_path: str):
    """
    Reads a copy list and checks if the files are correctly copied.
    """
    setup_logging(f"check_files")
    logger = logging.getLogger(__name__)

    logger.info(f"Reading copy list from {copy_list_path}")
    entries = []
    with open(copy_list_path, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f.readlines()):
            line = line.strip()
            if i > 1 and not line.startswith("#"):
                source, _, _, _, destination = line.split(";")
                entries.append((source, destination))

    logger.info(f"Checking {len(entries)} files")

    success_count = 0
    not_found_count = 0
    size_mismatch_count = 0
    total_source_size = 0
    total_destination_size = 0
    total_duplicate_size = 0
    total_duplicate_files = 0
    mismatched_files = []

    for source, destination in tqdm(entries, desc="Checking files"):
        source_path = Path(source)
        destination_path = Path(destination)

        if not source_path.exists():
            logger.warning(f"Source file not found: {source}")
            continue

        source_size = source_path.stat().st_size
        total_source_size += source_size

        file_found_and_size_matches = False
        destination_file_exists = False

        # Check original destination
        if destination_path.exists():
            destination_file_exists = True
            dest_size = destination_path.stat().st_size
            total_destination_size += dest_size
            if dest_size == source_size:
                file_found_and_size_matches = True

        # Use glob to find all duplicates at once, which is more efficient
        dup_pattern = str(
            destination_path.parent
            / (destination_path.stem + "_dup_*" + destination_path.suffix)
        )
        for dup_path_str in glob.glob(dup_pattern):
            dup_path = Path(dup_path_str)
            destination_file_exists = True
            dup_size = dup_path.stat().st_size
            total_destination_size += dup_size
            total_duplicate_size += dup_size
            total_duplicate_files += 1
            if not file_found_and_size_matches and dup_size == source_size:
                file_found_and_size_matches = True

        if file_found_and_size_matches:
            logger.debug(f"File check successful for {source}")
            success_count += 1
        else:
            if not destination_file_exists:
                logger.warning(f"File not found at destination: {destination}")
                not_found_count += 1
                mismatched_files.append(
                    {
                        "source": source,
                        "destination": destination,
                        "source_size": source_size,
                        "destination_size": "Not Found",
                    }
                )
            else:
                logger.warning(f"File size mismatch for {source} and {destination}.")
                size_mismatch_count += 1
                mismatched_files.append(
                    {
                        "source": source,
                        "destination": destination,
                        "source_size": source_size,
                        "destination_size": destination_path.stat().st_size,
                    }
                )

    logger.info("------ Check Summary ------")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Not found at destination: {not_found_count}")
    logger.info(f"Size mismatch: {size_mismatch_count}")

    logger.info("\n------ Size Statistics ------")
    logger.info(f"Total size of source files: {_format_size(total_source_size)}")
    logger.info(
        f"Total size of destination files: {_format_size(total_destination_size)}"
    )
    logger.info(f"Total duplicate files: {total_duplicate_files}")
    logger.info(f"Total size of duplicate files: {_format_size(total_duplicate_size)}")

    if mismatched_files:
        logger.info("\n------ Files with Size Mismatch ------")
        for f in mismatched_files:
            if f["destination_size"] == "Not Found":
                logger.info(
                    f"Source: {f['source']} ({_format_size(f['source_size'])}) - Destination file not found"
                )
            else:
                logger.info(
                    f"Source: {f['source']} ({_format_size(f['source_size'])}) - "
                    f"Destination: {f['destination']} ({_format_size(f['destination_size'])})"
                )
    logger.info("---------------------------------")
