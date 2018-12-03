import pytest

from aiogoogle.resource import Resource, GoogleAPI, Method
from aiogoogle import Aiogoogle
from ..test_globals import ALL_APIS


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_getitem(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert api['name'] == discovery_document.get('name')
    assert api['version'] == discovery_document.get('version')
    assert api['auth'] == discovery_document.get('auth')

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_properties(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert (name in str(api)) or (discovery_document.get('title') in str(api))
    assert (version in str(api)) or (discovery_document.get('title') in str(api))