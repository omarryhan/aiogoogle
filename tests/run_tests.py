import os, sys
import pytest
import time

SLEEP = 1.5

def main():
    test_integration = os.getenv('TEST_INTEGRATION')
    test_integration_with_keys = os.getenv('TEST_INTEGRATION_WITH_KEYS')

    if test_integration == 'true' and test_integration_with_keys == 'true':
        print('Running unit tests followed by integration tests and integration tests with keys provided')
        time.sleep(SLEEP)
        exit_code = pytest.main(
            [
                #'--fulltrace',
                '-v',
                '-s',
                '--maxfail=5',
                #'-p no:warnings',
                #'--disable-warnings',
                '--cov',
                'aiogoogle/',
                'tests/test_units/',
                'tests/test_integration/',
                'tests/test_integration_with_keys/',
            ]
        )
    elif test_integration == 'true':
        print('Running unit tests followed by asynchronous integration tests')
        time.sleep(SLEEP)
        exit_code = pytest.main(
            [
                '-v',
                '-s',
                #'--disable-warnings',
                #'--maxfail=5',
                '--cov',
                'aiogoogle/',
                'tests/test_units/',
                'tests/test_integration/'
            ]
        )
    else:
        print('Running unit tests')
        time.sleep(SLEEP)
        exit_code = pytest.main(
            [
                '-v',
                '-s',
                #'--disable-warnings',
                #'--maxfail=5',
                '--cov',
                'aiogoogle/',
                'tests/test_units/'
            ]
        )

    sys.exit(exit_code)

if __name__ == '__main__':
    main()