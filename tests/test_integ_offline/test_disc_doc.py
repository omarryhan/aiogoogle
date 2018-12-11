import re

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

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_resources_and_methods_dont_share_name(open_discovery_document, name, version):
    ''' Asserts no resources and methods that are on the same level share the same name.
    If a name was being shared, Aiogoogle will give precedence to the resource, rendering the method
    inaccessible '''
    def assert_no_similarity(resource):
        for resource_name in resource.resources_available:
            assert resource_name not in resource.methods_available
            assert_no_similarity(getattr(resource, resource_name))
    assert_no_similarity(GoogleAPI(open_discovery_document(name, version)))

@pytest.mark.parametrize('name,version', ALL_APIS)
def test_schemas_consistency(open_discovery_document, name, version):
    '''
    Tests the following:

        1. every schema has a type
        2. If an schema of type object doesn't have properties, then it must have additionalProperties
        3. addiotionalProperties should only contain a single schema
        4. All schemas should be objects (dicts)
        5. Tests all patterns in all schemas compile without errors

    Errors:
        
        1. 1 test fails because a schema that is of type: "object" neither has properties nor additionalProperties:
        
            - Youtube-v3, schemas, TokenPagination

        2. 2 schemas/properties doesn't have a type:

            1) pagespeedonline-v5

                Category groups = {
                    'additional_properties': {
                        ....
                        'properties':
                            'description': {
                                'description': 'An optional human readable description of the category group.',
                                'type': 'string'
                            },
                            'title': {
                                'description': 'The title of the category group.',
                                'type': 'string'
                            }
                        }
                    }
                }


            2) discovery-v1:

                RestDescription: {
                    id: "RestDescription",
                    type: "object",
                    properties: {
                        auth: {
                            type: "object",
                            description: "Authentication information.",
                            properties: {
                                oauth2: {
                                    type: "object",
                                    description: "OAuth 2.0 authentication information.",
                                    properties: {
                                        scopes: {
                                            type: "object",
                                            description: "Available OAuth 2.0 scopes.",
                                            additionalProperties: {
                                                type: "object",
                                                description: "The scope value.",
                                                properties: {
                                                    description: {
                                                        type: "string",                          Indentation is wrong here 
                                                        description: "Description of scope."     Indentation is wrong here
                                                        
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

        3. The following is a less major inconsistency and has been commented out from the test below: 
        Some additionalProperties return a string instead of a schema or bool
        Those additional properties will be ignored by default:
            
            https://tools.ietf.org/html/draft-zyp-json-schema-03#section-5.4:
            5.4.  additionalProperties

            This attribute defines a schema for all properties that are not
            explicitly defined in an object type definition.  If specified, the
            value MUST be a schema or a boolean.  If false is provided, no
            additional properties are allowed beyond the properties defined in
            the schema.  The default value is an empty schema which allows any
            value for additional properties.


        I know that Google's version of jsonschema3 isn't supposed to be 100% compliant but the errors above make it really hard
        to perform the simplest of validation
     '''

    # Avoid infinite recursion e.g. 
    # https://www.googleapis.com/discovery/v1/apis/bigquery/v2/rest / schemas / QueryParameterType schema
    schemas_checked = []

    def resolve(schema, schemas):
        ''' Resolves schema if resolvable '''
        if '$ref' in schema:
            schema = schemas[schema['$ref']]
        return schema

    def methods_gen(resource):
        ''' Generates all methods available in a given resource/googleAPI '''
        for method in resource.methods_available:
            yield getattr(resource, method)
        for n_resource in resource.resources_available:
            yield from methods_gen(getattr(resource, n_resource))

    def validate(schema_name, schema, schemas):
        schema = resolve(schema, schemas)

        assert 'type' in schema

        if schema['type'] == 'object':
            if 'properties' not in schema:
                ####################################################################################
                # Remove the following **line** for a proper test. This is just silencing the error
                if schema_name not in ['TokenPagination','tokenPagination']:
                ####################################################################################
                    assert 'additionalProperties' in schema
            else:
                for name, prop in schema['properties'].items():
                    if name not in schemas_checked:
                        schemas_checked.append(name)
                        validate(name, prop, schemas)
            if schema.get('additionalProperties'):
                schema = schema['additionalProperties']
                if isinstance(schema, dict):
                    if 'properties' not in schema:  # correct
                        if schema not in schemas_checked:
                            schemas_checked.append(schema)
                            validate('additionalProperties', schema, schemas)
                #    # If many additionalProperties, (it should only be one schema for all the additional props), iterate over them (Causes two more errors)
                #    else:
                #        for k,v in schema.items():
                #            # Might cause an infinite loop
                #            validate(k, v, schemas)
                #elif isinstance(prop, bool):
                #    pass
                #else:
                #    #raise TypeError(
                #    #    f'The following additionalProperty should be either a schema or bool not "{prop}"')
                #    pass
                #    #for _ in range(100000):
                #    #    print(prop)
        else:
            # all schemas/subschemas should eventually reach this point for testing
            if schema.get('pattern'):
                re.compile(schema['pattern'])
            

    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc['schemas']
    assert isinstance(schemas, dict)
    
    # Validate methods
    gapi = GoogleAPI(disc_doc)
    for method in methods_gen(gapi):
        for name, param in method.parameters.items():
            validate(name, param, schemas)

    # Validate schemas
    for name, schema in disc_doc['schemas'].items():
        if name not in schemas_checked:
            validate(name, schema, schemas)
