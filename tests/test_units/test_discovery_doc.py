import pytest

from aiogoogle import DiscoveryClient
from ..globals import SOME_APIS
from jsonschema import Draft4Validator, Draft3Validator

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_parameters_not_included_twice(open_discovery_document, name, version):
    ''' 
    I was curious whether global parameters might have identical names
    to ResourceMethod.parameters.
    Fails if collision found
    '''
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(client.resources, resource_name)
        for method_name in resource.methods:
            resource_method = getattr(resource, method_name)
            for parameter_name, _ in resource_method._method_specs.get('parameters', {}).items():
                assert parameter_name not in resource_method._global_parameters

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_schemas_adhering_jsonschema_v4(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    for _, schema in discovery_document.get('schemas', {}).items():
        Draft3Validator.check_schema(schema)
