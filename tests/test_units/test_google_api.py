import pytest

from aiogoogle import Aiogoogle
from aiogoogle.resource import Resource, GoogleAPI, Method, STACK_QUERY_PARAMETER_DEFAULT_VALUE, STACK_QUERY_PARAMETERS
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

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert id(api.discovery_document) == id(api.discovery_document)
    assert api['resources'] == discovery_document.get('resources')

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_getattr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource_object = getattr(api, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_repr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    name = discovery_document.get('name')
    version = discovery_document.get('version')
    base_url = discovery_document.get('baseUrl')
    assert name in str(api) and version in str(api) and base_url in str(api)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_len(open_discovery_document, name, version):
	discovery_document = open_discovery_document(name, version)
	api = GoogleAPI(discovery_document=discovery_document)
	methods_len = len(discovery_document.get('methods')) if discovery_document.get('methods') else 0
	resources_len = len(discovery_document.get('resources')) if discovery_document.get('resources') else 0
	assert len(api) == methods_len + resources_len

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resources_getattr_fails_on_unknown_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    nonexistent_resource = 'I_MUST_NEVER_EXIST_ANYWHEREEEEEEEE'
    with pytest.raises(AttributeError) as e:
        getattr(api, nonexistent_resource)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_add_global_params(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for param in STACK_QUERY_PARAMETERS:
        assert param in api['parameters']
        assert api['parameters'][param] == STACK_QUERY_PARAMETER_DEFAULT_VALUE
