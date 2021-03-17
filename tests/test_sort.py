#!/usr/bin/env python3

from testsupport import run_project_executable, run, assert_executable, info, warn
from wiki import download_wiki
from tempfile import TemporaryDirectory
from pathlib import Path
import sys


def main() -> None:
    path = download_wiki("scowiki-latest-all-titles-in")

    assert_executable("sort", "This test requires 'sort' command line tool")
    assert_executable("cmp", "This test requires 'cmp' command line tool")

    with TemporaryDirectory() as tempdir:
        temp_path = Path(tempdir)
        coreutils_sort = temp_path.joinpath(path.name + ".coreutils-sort")
        own_sort = temp_path.joinpath(path.name + ".own-sort")

        info("Run coreutils sort...")
        with open(path) as stdin, open(coreutils_sort, "w") as stdout:
            run(["sort"], stdin=stdin, stdout=stdout, extra_env=dict(LANG="C"))
        info("OK")

        info("Run own sort...")
        try:
            with open(path) as stdin, open(own_sort, "w") as stdout:
                run_project_executable("sort", stdin=stdin, stdout=stdout)
        except OSError as e:
            warn(f"Failed to run command: {e}")
            info("FAIL")
            sys.exit(1)
        info("OK")

        info("Check if both results matches")
        try:
            run(["cmp", str(coreutils_sort), str(own_sort)], extra_env=dict(LANG="C"))
        except OSError as e:
            warn(f"coreutils sort and own sort produce different output: {e}")
            info("FAIL")
            sys.exit(1)

        info("OK")


if __name__ == "__main__":
    main()
