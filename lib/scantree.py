import os
from pathlib import Path


def scantree(path):
    if Path(path).is_dir():
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                yield from scantree(entry.path)
            else:
                yield entry
