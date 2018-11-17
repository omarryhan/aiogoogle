import os
import json

import pytest

from aiogoogle.models import Request


@pytest.fixture('function')
def open_discovery_document():
    def wrapped(name, version):
        current_dir = os.getcwd()
        file_name = current_dir + '/tests/data/' + name + '_' + version + '_discovery_doc.json'
        with open(file_name, 'r') as discovery_doc:
            discovery_doc_dict = json.loads(discovery_doc.read())
        return discovery_doc_dict
    return wrapped
