import pytest

import pprint
from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod
from ..globals import SOME_APIS


@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_class_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    assert id(client.discovery_document) == id(client.resources.discovery_document)
    assert client.resources._resources_specs == discovery_document.get('resources')

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_getattr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, resource_methods in discovery_document.get('resources').items():
        resource_object = getattr(client.resources, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_repr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    available_resources_names = [k for k,v in discovery_document.get('resources').items()] if discovery_document.get('resources') else None
    assert str(available_resources_names) in str(client.resources)

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_len(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    true_len = len(discovery_document.get('resources')) if discovery_document.get('resources') else 0
    assert len(client.resources) == true_len

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resources_getattr_fails_on_unknown_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)

    nonexistent_resource = 'I_MUST_NEVER_EXIST_ANYWHEREEEEEEEE'

    with pytest.raises(AttributeError) as e:
        getattr(client.resources, nonexistent_resource)

    documentation_link = client.discovery_document.get('documentationLink') or 'https://developers.google.com/'
    assert f"Resource doesn't exist. Check: {documentation_link} for more info" in str(e)
