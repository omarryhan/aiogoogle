#!/usr/bin/python3

import os, sys
import pytest

args = [
    '-v',
    '-s',
    '--cov',
    'aiogoogle/',
    #'--tb=long',
    #'--fulltrace',
    #'--maxfail=5',
    #'-p no:warnings',
    #'--disable-warnings',
]

def main():

    if os.getenv('TEST_UNITS') == 'true':
        args.append(
            'tests/test_units/',
        )
    if os.getenv('TEST_INTEGRATION_OFFLINE') == 'true':
        args.append(
            'tests/test_integ_offline/',
        )
    if os.getenv('TEST_INTEGRATION_ONLINE') == 'true':
        args.append(
            'tests/test_integ_online/',
        )
    if os.getenv('TEST_INTEGRATION_WITH_KEYS') == 'true':
        args.append(
            'tests/test_with_keys/'
        )
    sys.exit(pytest.main(args))

if __name__ == '__main__':
    main()