import os
import errno
import json

import pytest

from aiogoogle import DiscoveryClient
from ..globals import SOME_APIS


@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', SOME_APIS)
async def test_download_discovery_client(name, version):
    discovery_client = DiscoveryClient()
    await discovery_client.discover(name, version)
    assert isinstance(discovery_client.discovery_document, dict)
    assert len(discovery_client.discovery_document) >= 1

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', SOME_APIS)
async def test_save_docs_as_json(name, version):
    discovery_client = DiscoveryClient()

    # Download discovery document
    await discovery_client.discover(name, version)

    # Create new .data/ dir if it doesn't exists
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
        json.dump(discovery_client.discovery_document, discovery_file)

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_load_docs_as_dict(open_discovery_document, name, version):
    doc = open_discovery_document(name, version)
    assert isinstance(doc, dict)
    assert doc

