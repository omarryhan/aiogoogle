#!/usr/bin/python3

import os
import sys
import pytest

args = [
    "-v",
    "-s",
    "--cov",
    "aiogoogle/",
    # "-vv",
    # '--tb=long',
    # '--fulltrace',
    # '--maxfail=5',
    # '-p no:warnings',
    # '--disable-warnings',
]


def main():

    if os.getenv("TEST_UNITS") == "true":
        args.append("tests/test_units/")
    if os.getenv("TEST_INTEGRATION") == "true":
        args.append("tests/test_integration/")
    sys.exit(pytest.main(args))


if __name__ == "__main__":
    main()
