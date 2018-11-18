import os
import json

import pytest

from aiogoogle.models import Request
from aiogoogle import DiscoveryClient


@pytest.fixture('function')
def open_discovery_document():
    def wrapped(name, version):
        current_dir = os.getcwd()
        file_name = current_dir + '/tests/data/' + name + '_' + version + '_discovery_doc.json'
        with open(file_name, 'r') as discovery_doc:
            discovery_doc_dict = json.loads(discovery_doc.read())
        return discovery_doc_dict
    return wrapped

@pytest.fixture('function')
def create_client(open_discovery_document):
    def wrapped(name, version):
        disc_doc = open_discovery_document(name, version)
        client = DiscoveryClient(discovery_document=disc_doc)
        return client
    return wrapped