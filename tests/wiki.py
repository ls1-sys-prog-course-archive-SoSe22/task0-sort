#!/usr/bin/env python3

from testsupport import test_root, ensure_download
from pathlib import Path
import gzip
import os
import shutil

URL_PREFIX = "https://github.com/Mic92/wiki-topics/releases/download/assets/"


def download_wiki(name: str) -> Path:
    compressed = test_root().joinpath(name + ".gz")
    uncompressed = test_root().joinpath(name)
    uncompressed_temp = test_root().joinpath(name + ".tmp")
    ensure_download(f"{URL_PREFIX}/{name}.gz", compressed)
    if uncompressed.exists():
        return uncompressed

    with gzip.open(compressed, "rb") as f_in, open(uncompressed_temp, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
        os.rename(uncompressed_temp, uncompressed)
    return uncompressed
