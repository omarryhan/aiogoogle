import os
import errno
import json

import pytest

from aiogoogle import Aiogoogle
from ..globals import SOME_APIS

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', SOME_APIS)
async def test_download_aiogoogle_without_version(name, version):
    aiogoogle = Aiogoogle()
    google_api = await aiogoogle.discover(name)
    assert google_api.discovery_document['name'] == name
    #assert google_api.discovery_document['version'] == version

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', SOME_APIS)
async def test_download_aiogoogle(name, version):
    aiogoogle = Aiogoogle()
    google_api = await aiogoogle.discover(name, version)
    assert google_api.discovery_document

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', SOME_APIS)
async def test_save_docs_as_json(name, version):
    #TODO: Change this to be a conftest
    aiogoogle = Aiogoogle()

    # Download discovery document
    google_api = await aiogoogle.discover(name, version)

    # Create new .data/ dir if one doesn't exists
    current_dir = os.getcwd()
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

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_load_docs_as_dict(open_discovery_document, name, version):
    doc = open_discovery_document(name, version)
    assert isinstance(doc, dict)
    assert doc

