#!/usr/bin/python3.7

from test_globals import ALL_APIS
from aiogoogle import Aiogoogle
import os, sys
import errno
import json
import asyncio
from aiohttp import ClientSession
import pprint

async def refresh_disc_docs_json():

    file_errors = []

    # Create new .data/ dir if one doesn't exists
    current_dir = os.getcwd()
    if current_dir[-9:] != 'aiogoogle':  # current dir is aiogoogle
        print(current_dir)
        print("must be in aiogoogle's dir, not test dir")
        sys.exit()

    # Refresh ALL_APIS in tests/tests_globals.py
    ALL_APIS = []
    print('Refreshing ALL_APIS in tests_globals.py')
    async with ClientSession() as sess:
        apis_pref = await sess.get('https://www.googleapis.com/discovery/v1/apis?preferred=true')
        apis_pref = await apis_pref.json()
    for api in apis_pref['items']:
        ##############################
        # Remove me 
            #  https://www.googleapis.com/discovery/v1/apis/partners/v2/rest 
            # raises 502 as of datetime.datetime(2018, 12, 1, 17, 46, 38, 39391)
        if api['name'] != 'partners':
        # /Remove me
        ##############################
            ALL_APIS.append((api['name'], api['version']))
    with open('tests/test_globals.py', 'w') as f:
        f.write(f'ALL_APIS = {pprint.pformat(ALL_APIS)}')
        print('SUCCESS!')

    # Refresh discovery files in tests/data
    for name, version in ALL_APIS:
        aiogoogle = Aiogoogle()
        print(f'Downloading {name}-{version}')
        try:
            google_api = await aiogoogle.discover(name, version)
        except Exception as e:
            file_errors.append(
                {
                    f'{name}-{version}': str(e)
                }
            )
            continue

        data_dir_name = current_dir + '/tests/data/'
        try:
            if not os.path.exists(data_dir_name):
                os.makedirs(data_dir_name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        # Save discovery docuemnt as .json file to the newly created data dir
        file_name = current_dir + '/tests/data/' + name + '_' + version + '_discovery_doc.json'
        with open(file_name, 'w') as discovery_file:
            json.dump(google_api.discovery_document, discovery_file)
        print(f'saved {name}-{version} to {file_name}')
    
    print('Done')
    if file_errors:
        print(f'Errors found: {str(file_errors)}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(refresh_disc_docs_json())