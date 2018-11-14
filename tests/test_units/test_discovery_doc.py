import pytest

from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod
from ..globals import some_apis


def test_discovery_client():
    DiscoveryClient()

@pytest.mark.parametrize('name,version', some_apis)
def test_discovery_setter(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    assert client.name == discovery_document.get('name')
    assert client.version == discovery_document.get('version')
    assert client._schema == discovery_document.get('schema')
    assert client._auth == discovery_document.get('auth')
    assert client._global_parameters == discovery_document.get('parameters')
    assert isinstance(client.resources, Resources)

@pytest.mark.parametrize('name,version', some_apis)
def test_resources_class_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    assert id(client.discovery_document) == id(client.resources.discovery_document)
    assert id(client._schema) == id(client.resources._schema)
    assert id(client._auth) == id(client.resources._auth)
    assert id(client._global_parameters) == id(client.resources._global_parameters)
    assert client.resources._resources == discovery_document.get('resources')

@pytest.mark.parametrize('name,version', some_apis)
def test_resources_getattr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, resource_methods in discovery_document.get('resources').items():
        resource_object = getattr(client.resources, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name
    
@pytest.mark.parametrize('name,version', some_apis)
def test_resources_getattr_fails_on_unknown_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)

    nonexistent_resource = 'I_MUST_NEVER_EXIST_ANYWHEREEEEEEEE'

    with pytest.raises(AttributeError) as e:
        getattr(client.resources, nonexistent_resource)

    documentation_link = client.discovery_document.get('documentationLink') or 'https://developers.google.com/'
    assert f"Resource doesn't exist. Check: {documentation_link} for more info" in str(e)

@pytest.mark.parametrize('name,version', some_apis)
def test_resource_class_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, resource_methods in discovery_document.get('resources').items():
        resource_object = getattr(client.resources, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name
        assert resource_object._resource == discovery_document['resources'][resource_name]
        assert resource_object._global_parameters == discovery_document.get('parameters')
        assert resource_object._schema == discovery_document.get('schema')

def test_resource_get_nested_resources_method():
    resource = Resource(
        name='irrelevant',
        resource={
            'resources': {
                'first_resource': 1,
                'second_resource': 2
            },
            'methods': {
                'third_method': 3,
                'forth_method': 4
            }
        }
    )
    assert 'first_resource' in resource.nested_resources
    assert 'second_resource' in resource.nested_resources

def test_resource_available_methods():
    resource = Resource(
        name='irrelevant',
        resource={
            'resources': {
                'first_resource': 1,
                'second_resource': 2
            },
            'methods': {
                'third_method': 3,
                'forth_method': 4
            }
        }
    )
    assert 'third_method' in resource.available_methods
    assert 'forth_method' in resource.available_methods

@pytest.mark.parametrize('name,version', some_apis)
def test_resource_returns_nested_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources', {}).items():
        resource = getattr(client.resources, resource_name)
        if resource.nested_resources:
            # Assert that it returns resources not methods
            for nested_resource_name in resource.nested_resources:
                nested_resource = getattr(resource, nested_resource_name)
                assert isinstance(nested_resource, Resource)

@pytest.mark.parametrize('name,version', some_apis)
def test_resource_returns_available_methods(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources', {}).items():
        resource = getattr(client.resources, resource_name)
        if resource.available_methods:
            # Assert that it returns resources not methods
            for available_method_name in resource.available_methods:
                available_method = getattr(resource, available_method_name)
                assert isinstance(available_method, ResourceMethod)
