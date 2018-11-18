import pytest

import pprint
from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod
from ...globals import SOME_APIS


@pytest.mark.parametrize('name,version', SOME_APIS)
def test_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            for parameter_name, _ in resource_method.parameters.items():
                assert (
                    parameter_name in discovery_document.get('parameters') or 
                    parameter_name in discovery_document['resources'][resource_name]['methods'][method_name]['parameters']
                ) 

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_optional_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            for parameter_name in resource_method.optional_parameters:
                parameter = resource_method.parameters[parameter_name]
                assert parameter.get('required') is not True

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_required_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            for parameter_name in resource_method.required_parameters:
                parameter = resource_method.parameters[parameter_name]
                assert parameter.get('required') is True

# TODO:
# test_path_parameteres
# test_query_parameters
# test_required_query_parameters
# test_optional_query_parameters

def test_getattr():
    resource_method = ResourceMethod(
        name='IRRELEVANT',
        method_specs={
            'am_i_here_1': True,
            'am_i_here_2': None
        },
        global_parameters='IRRELEVANT',
        schemas={'IRRELEVANT': 'IRRELEVANT'},
        base_url='IRRELEVANT',
        root_url='IRRELEVANT',
        validate = False 
    )

    assert resource_method.am_i_here_1 is True
    assert resource_method.am_i_here_2 is None
    with pytest.raises(AttributeError):
        resource_method.i_dont_exist

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_len(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            assert isinstance(len(resource_method), int)

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_str_repr(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            assert str(resource_method)
