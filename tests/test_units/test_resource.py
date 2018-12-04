import pytest

from aiogoogle import Aiogoogle
from aiogoogle.resource import Resource, GoogleAPI, Method, STACK_QUERY_PARAMETER_DEFAULT_VALUE, STACK_QUERY_PARAMETERS
from ..test_globals import ALL_APIS

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resource_constructor(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource_object = getattr(api, resource_name)
        assert isinstance(resource_object, Resource)
        assert resource_name == resource_object.name
        assert resource_object._resource_specs == discovery_document['resources'][resource_name]
        assert resource_object._global_parameters == discovery_document.get('parameters')
        assert resource_object._schemas == discovery_document.get('schemas')
        ##
        assert api['schemas'] is resource_object._schemas
        assert api['parameters'] is resource_object._global_parameters

def test_resources_available_property():
    resource = Resource(
        name='irrelevant',
        resource_specs={
            'resources': {
                'first_resource': 1,
                'second_resource': 2
            },
            'methods': {
                'third_method': 3,
                'forth_method': 4
            }
        },
        global_parameters = None,
        schemas = None,
        batch_path = None,
        root_url = None,
        validate = False,
        service_path = None
    )
    assert 'first_resource' in resource.resources_available
    assert 'second_resource' in resource.resources_available

def test_methods_available_property():
    resource = Resource(
        name='irrelevant',
        resource_specs={
            'resources': {
                'first_resource': 1,
                'second_resource': 2
            },
            'methods': {
                'third_method': 3,
                'forth_method': 4
            }
        },
        global_parameters = None,
        schemas = None,
        batch_path = None,
        root_url = None,
        validate = False,
        service_path = None
    )
    assert 'third_method' in resource.methods_available
    assert 'forth_method' in resource.methods_available

def test_resource_len():
    resource = Resource(
        name='irrelevant',
        resource_specs={
            'resources': {
                'first_resource': 1,
                'second_resource': 2,
                'basdasd': 239
            },
            'methods': {
                'third_method': 3,
                'forth_method': 4
            }
        },
        global_parameters = None,
        schemas = None,
        root_url = None,
        batch_path = None,
        validate = False,
        service_path = None
    )
    assert len(resource) == 2

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resource_returns_nested_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources', {}).items():
        resource = getattr(api, resource_name)
        if resource.resources_available:
            # Assert that it returns resources not methods
            for nested_resource_name in resource.resources_available:
                nested_resource = getattr(resource, nested_resource_name)
                assert isinstance(nested_resource, Resource)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resource_returns_available_methods(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources', {}).items():
        resource = getattr(api, resource_name)
        if resource.methods_available:
            # Assert that it returns resources not methods
            for available_method_name in resource.methods_available:
                available_method = getattr(resource, available_method_name)
                assert isinstance(available_method, Method)


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_method_construction(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            # Assert a resource has the returned method
            assert method.name in discovery_document['resources'][resource_name]['methods']
            # Assert specs belong to the created method
            assert method._method_specs == discovery_document['resources'][resource_name]['methods'][method_name]
            # Assert global parameters were passed correctly
            assert method._global_parameters == discovery_document.get('parameters')
            # Assert schemas where passed correctly
            assert method._schemas == discovery_document.get('schemas')

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resource_construction(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for nested_resource_name in resource.resources_available:
            nested_resource = getattr(resource, nested_resource_name)
            assert isinstance(nested_resource, Resource)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_calling_resource_fails(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        with pytest.raises(TypeError):
            resource()

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_str_resource(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        assert discovery_document['rootUrl'] in str(resource)
        assert 'resource' in str(resource)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_stack_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for param_name in STACK_QUERY_PARAMETERS:
            assert param_name in resource._global_parameters
            assert resource._global_parameters[param_name] == STACK_QUERY_PARAMETER_DEFAULT_VALUE


