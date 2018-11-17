import pytest

import pprint
from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod
from ..globals import SOME_APIS


@pytest.mark.parametrize('name,version', SOME_APIS)
def test_resource_method_parameters(open_discovery_document, name, version):
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
def test_resource_method_optional_parameters(open_discovery_document, name, version):
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
def test_resource_method_required_parameters(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            for parameter_name in resource_method.required_parameters:
                parameter = resource_method.parameters[parameter_name]
                assert parameter.get('required') is True
