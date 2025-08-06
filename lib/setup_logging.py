import sys
import logging


def setup_logging(name, stdout_level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s | %(process)d | %(levelname)s | %(name)s | %(message)s"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(stdout_level)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{name}-debug.txt", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    logging.getLogger("lib.dateparser.dateparser").setLevel(logging.INFO)
