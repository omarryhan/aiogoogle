import pytest

from aiogoogle import Aiogoogle
from aiogoogle.resource import RESERVED_KEYWORDS, GoogleAPI
from aiogoogle.validate import KNOWN_FORMATS, JSON_PYTHON_TYPE_MAPPING
from ..test_globals import ALL_APIS


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_parameters_not_included_twice(open_discovery_document, name, version):
    ''' 
    I was curious whether global parameters might have identical names
    with Method.parameters.
    Fails if similarities found
    '''
    discovery_document = open_discovery_document(name, version)
    google_api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(google_api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            local_params = method['parameters'] or {}
            for parameter_name, _ in local_params.items():
                assert parameter_name not in method._global_parameters

# FAILS (Mainly because it expects minimum and maximum to be ints not str e.g. 10 not "10")
#
#from jsonschema import Draft3Validator
#
#@pytest.mark.parametrize('name,version', ALL_APIS)
#def test_schemas_adhering_jsonschema_v4(open_discovery_document, name, version):
#    discovery_document = open_discovery_document(name, version)
#    for _, schema in discovery_document.get('schemas', {}).items():
#        Draft3Validator.check_schema(schema)
#
#
#@pytest.mark.parametrize('name,version', ALL_APIS)
#def test_methods_schemas_adhering_jsonschema_v4(open_discovery_document, name, version):
#
#    def check_schema(methods):
#        for _,method in methods.items():
#            if method.get('parameters'):
#                for _, parameter in method['parameters'].items():
#                    if parameter:
#                        Draft3Validator.check_schema(parameter)
#
#    def resolve_resource(resource):
#        if resource.get('methods'):
#            check_schema(resource['methods'])
#        if resource.get('resources'):
#            for _,resource in resource['resources'].items():
#                resolve_resource(resource)
#
#    discovery_document = open_discovery_document(name, version)
#    for _, resource in discovery_document['resources'].items():
#        resolve_resource(resource)


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_parameters_not_colliding_with_google_api__call__(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    google_api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(google_api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            params = method.parameters
            for param_name, _ in params.items():
                assert param_name not in RESERVED_KEYWORDS


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_parameters_not_colliding_with_google_api__call__fails(open_discovery_document, name, version):
    ''' asserts previous test catches collisions if any'''

    COLLIDING_RESERVED_KEYWORDS = ['alt', 'part']

    class CollisionError(Exception):
        pass
    
    def check_collision(param_name):
        if param_name in COLLIDING_RESERVED_KEYWORDS:
            raise CollisionError()

    discovery_document = open_discovery_document(name, version)
    google_api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(google_api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            params = method.parameters
            with pytest.raises(CollisionError):
                for param_name, _ in params.items():
                    check_collision(param_name)


@pytest.mark.parametrize('name,version', ALL_APIS)
def test_properties_only_in_objects_not_any_other_type(open_discovery_document, name, version):
    '''
    Disc doc sanity check.
    Checks if objects are the only google-jsonschema type that has a an attribute call "Properties"
    '''
    discovery_document = open_discovery_document(name, version)
    google_api = GoogleAPI(discovery_document=discovery_document)
    if google_api.discovery_document.get('schemas'):
        for _,v in google_api.discovery_document['schemas'].items():
            if v['type'] != 'object':
                assert not v.get('properties')

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_items_must_be_in_array_type(open_discovery_document, name, version):
    ''' Test that all array types in disc docs have an attribute called "items".
    aiogoogle.validate.validate assumes all arrays has an "items" property and it will 
    fail if it didn't find one '''
    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc['schemas']

    def resolve(schema):
        if '$ref' in schema:
            return schemas[schema['$ref']]
        else:
            return schema

    for _, schema in disc_doc['schemas'].items():
        if 'properties' in schema:  # 6 failures without this check
            for _, prop in schema['properties'].items():
                prop = resolve(prop)
                if prop['type'] == 'array':
                    assert 'items' in prop

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_schemas_for_unknown_formats_and_types(open_discovery_document, name, version):
    ''' Iterates over all available disc docs and checks all schemas if they have any unknown types or 
    formats other than the ones mentioned in discovery service's documentation
    aiogoogle.validate.KNOWN_FORMATS and keys of aiogoogle.validate.JSON_PYTHON_TYPE_MAPPING '''
    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc['schemas']
    resources = disc_doc['resources']

    def resolve(schema):
        if '$ref' in schema:
            return schemas[schema['$ref']]
        else:
            return schema

    # schemas
    for _, schema in schemas.items():
        if 'properties' in schema:  # 6 failures without this check
            for _, prop in schema['properties'].items():
                prop = resolve(prop)
                assert prop['type'] in JSON_PYTHON_TYPE_MAPPING
                if 'format' in prop:
                    assert prop['format'] in KNOWN_FORMATS

    # methods
    # Doesn't cover all methods as this assumes the following heierarchy api.resource.method and doesn't check for any other combination
    # However, this should cover a fair part of most APIs
    for _, resource in resources.items():
        if 'methods' in resource:
            for _, method in resource['methods'].items():
                if 'parameters' in method:
                    for _, param in method['parameters'].items():
                        param = resolve(param)
                        assert param['type'] in JSON_PYTHON_TYPE_MAPPING
                        if 'format' in param:
                            assert param['format'] in KNOWN_FORMATS
        

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_parameters_are_not_objects(open_discovery_document, name, version):
    ''' 
    I was curious whether global parameters might have identical names
    with Method.parameters.
    Fails if similarities found
    '''
    discovery_document = open_discovery_document(name, version)
    google_api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get('resources').items():
        resource = getattr(google_api, resource_name)
        for method_name in resource.methods_available:
            method = getattr(resource, method_name)
            if method.parameters:
                for _,v in method.parameters.items():
                    assert v.get('type') != 'object' 
                    assert not v.get('properties')

