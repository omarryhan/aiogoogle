import pytest

import pprint
from aiogoogle import Aiogoogle
from aiogoogle.resource import Resource, GoogleAPI, Method
from ..globals import SOME_APIS


@pytest.mark.parametrize('name,version', SOME_APIS)
def test_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert id(api.discovery_document) == id(api.discovery_document)
    assert api['resources'] == discovery_document.get('resources')

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_getattr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource_object = getattr(api, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_repr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    available_resources_names = [k for k,v in discovery_document.get('resources').items()] if discovery_document.get('resources') else None
    assert str(available_resources_names) in str(api)

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_len(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    true_len = len(discovery_document.get('resources')) if discovery_document.get('resources') else 0
    assert len(api) == true_len

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_getattr_fails_on_unknown_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)

    nonexistent_resource = 'I_MUST_NEVER_EXIST_ANYWHEREEEEEEEE'

    with pytest.raises(AttributeError) as e:
        getattr(api, nonexistent_resource)

    documentation_link = api.discovery_document.get('documentationLink') or 'https://developers.google.com/'
    assert f"Resource doesn't exist. Check: {documentation_link} for more info" in str(e)
