#!/usr/bin/env python3

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
from shlex import quote
from typing import Any, IO

from testsupport import (
    assert_executable,
    info,
    run,
    warn,
    project_path,
    find_executable,
)
from wiki import download_wiki


def run_with_ulimit(exe: str, stdin: IO[Any], stdout: IO[Any]) -> None:
    # size is in kilobytes
    size = 128 * 1024
    run(
        [f"ulimit -v {quote(str(size))}; {quote(str(exe))}"],
        stdin=stdin,
        stdout=stdout,
        extra_env=dict(LC_ALL="C"),
        shell=True,
    )


def main() -> None:
    path = download_wiki("en-latest-all-titles-in")

    assert_executable("sort", "This test requires 'sort' command line tool")
    assert_executable("cmp", "This test requires 'cmp' command line tool")

    own_sort_exe = find_executable("sort", project_path())
    if own_sort_exe is None:
        warn(f"executable 'sort' not found in {project_path()}")
        sys.exit(1)

    with TemporaryDirectory() as tempdir:
        temp_path = Path(tempdir)
        coreutils_sort = temp_path.joinpath(path.name + ".coreutils-sort")
        own_sort = temp_path.joinpath(path.name + ".own-sort")

        info("Run coreutils sort...")
        with open(path) as stdin, open(coreutils_sort, "w") as stdout:
            run_with_ulimit("sort", stdin, stdout)
        info("OK")

        info("Run own sort...")
        try:
            with open(path) as stdin, open(own_sort, "w") as stdout:
                run_with_ulimit("sort", stdin, stdout)
        except OSError as e:
            warn(f"Failed to run command: {e}")
            info("FAIL")
            sys.exit(1)
        info("OK")

        info("Check if both results matches")
        try:
            run(["cmp", str(coreutils_sort), str(own_sort)])
        except subprocess.CalledProcessError as e:
            warn(f"coreutils sort and own sort produce different output: {e}")
            info("FAIL")
            sys.exit(1)

        info("OK")


if __name__ == "__main__":
    main()
