import pytest

from aiogoogle import Aiogoogle
from aiogoogle.resource import Resource, GoogleAPI, Method, STACK_QUERY_PARAMETER_DEFAULT_VALUE, STACK_QUERY_PARAMETERS
from ..test_globals import ALL_APIS


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for parameter_name, _ in method.parameters.items():
                assert (
                    parameter_name in discovery_document.get('parameters') or 
                    parameter_name in discovery_document['resources'][resource_name]['methods'][method_name]['parameters']
                ) 

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_optional_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for parameter_name in method.optional_parameters:
                parameter = method.parameters[parameter_name]
                assert parameter.get('required') is not True

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_required_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for parameter_name in method.required_parameters:
                parameter = method.parameters[parameter_name]
                assert parameter.get('required') is True

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_path_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for parameter_name in method.path_parameters:
                parameter = method.parameters[parameter_name]
                assert parameter.get('location') == 'path'

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_query_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for parameter_name in method.query_parameters:
                parameter = method.parameters[parameter_name]
                assert parameter.get('location') == 'query'

def test_getitem():
    method = Method(
        name='IRRELEVANT',
        method_specs={
            'am_i_here_1': True,
            'am_i_here_2': None
        },
        global_parameters={'IRRELEVANT': 'IRRELAVANT'},
        schemas={'IRRELEVANT': 'IRRELEVANT'},
        batch_path='IRRELEVANT',
        root_url='IRRELEVANT',
        service_path='IRRELEVANT',
        validate = False 
    )

    assert method['am_i_here_1'] is True
    assert method['am_i_here_2'] is None
    assert method['i_dont_exist'] is None

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_len(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            assert isinstance(len(method), int)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_str_repr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            assert str(method)

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_stack_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            for stack_param_name in STACK_QUERY_PARAMETERS:
                assert stack_param_name in method.optional_parameters
                assert stack_param_name in method.parameters
