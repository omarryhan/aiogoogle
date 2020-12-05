import re

import pytest

from aiogoogle import Aiogoogle
from aiogoogle.resource import RESERVED_KEYWORDS
from aiogoogle.validate import KNOWN_FORMATS, JSON_PYTHON_TYPE_MAPPING
from aiogoogle.auth.managers import OPENID_CONFIGS_DISCOVERY_DOC_URL as openid_url
from aiogoogle.auth.data import WELLKNOWN_OPENID_CONFIGS as currunt_openid_configs
from ..ALL_APIS import ALL_APIS

from aiohttp import ClientSession


@pytest.mark.asyncio
async def test_oauth2_manager_api_is_latest_version():
    CURRENT_OAUTH2_API_VERSION = 2
    async with Aiogoogle() as google:
        oauth2_apis_list = await google.list_api("oauth2")
    apis = oauth2_apis_list["items"]
    versions_available = [int(api["version"][-1:]) for api in apis]
    for version in versions_available:
        assert CURRENT_OAUTH2_API_VERSION >= version


@pytest.mark.asyncio
async def test_hardcoded_discovery_service_api_specs_is_latest_version():
    CURRENT_VERSION = 1
    async with Aiogoogle() as google:
        discovery_apis_list = await google.list_api("discovery")
    apis = discovery_apis_list["items"]
    versions_available = [int(api["version"][-1:]) for api in apis]
    for version in versions_available:
        assert CURRENT_VERSION >= version


@pytest.mark.asyncio
async def test_latest_openid_configs():
    async with ClientSession() as sess:
        new_configs_res = await sess.get(openid_url)
        new_configs = await new_configs_res.json()

        new_config_keys = list(new_configs.keys())
        currunt_openid_configs_keys = list(currunt_openid_configs.keys())

        new_config_keys.sort()
        currunt_openid_configs_keys.sort()

        assert new_config_keys == currunt_openid_configs_keys
        assert len(new_config_keys) == len(currunt_openid_configs_keys)
        for k in new_config_keys:
            assert new_configs[k] == currunt_openid_configs[k]


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_parameters_not_included_twice(name, version, methods_generator):
    """ 
    I was curious whether global parameters might have identical names
    as Method.parameters.
    Fails if similarities found
    """
    for method in methods_generator(name, version):
        local_params = method["parameters"] or {}
        for parameter_name, _ in local_params.items():
            assert parameter_name not in method._global_parameters


@pytest.mark.skip(reason="Fails with Apigee-v1 (todo: find a solution without breaking the API)")
@pytest.mark.parametrize("name,version", ALL_APIS)
def test_parameters_not_colliding_with_google_api__call__(
    name, version, methods_generator
):
    for method in methods_generator(name, version):
        params = method.parameters
        for param_name, _ in params.items():
            assert param_name not in RESERVED_KEYWORDS


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_parameters_not_colliding_with_google_api__call__fails(
    name, version, methods_generator
):
    """ asserts previous test catches collisions if any"""

    COLLIDING_RESERVED_KEYWORDS = ["alt", "part"]

    class CollisionError(Exception):
        pass

    def check_collision(param_name):
        if param_name in COLLIDING_RESERVED_KEYWORDS:
            raise CollisionError()

    for method in methods_generator(name, version):
        params = method.parameters
        with pytest.raises(CollisionError):
            for param_name, _ in params.items():
                check_collision(param_name)


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_properties_only_in_objects_not_any_other_type(create_api, name, version):
    """
    Disc doc sanity check.
    Checks if objects are the only google-jsonschema type that has an attribute called "Properties"
    """
    google_api = create_api(name, version)
    if google_api.discovery_document.get("schemas"):
        for _, v in google_api.discovery_document["schemas"].items():
            if v["type"] != "object":
                assert not v.get("properties")


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_items_must_be_in_array_type(open_discovery_document, name, version):
    """ Test that all array types in disc docs have an attribute called "items".
    aiogoogle.validate.validate assumes all arrays has an "items" property and it will 
    fail if it didn't find one """
    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc["schemas"]

    def resolve(schema):
        if "$ref" in schema:
            return schemas[schema["$ref"]]
        else:
            return schema

    for _, schema in disc_doc["schemas"].items():
        if "properties" in schema:  # 6 failures without this check
            for _, prop in schema["properties"].items():
                prop = resolve(prop)
                if prop["type"] == "array":
                    assert "items" in prop


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_schemas_for_unknown_formats_and_types(open_discovery_document, name, version, methods_generator):
    """ Iterates over all available disc docs and checks all schemas if they have any unknown types or 
    formats other than the ones mentioned in discovery service's documentation
    aiogoogle.validate.KNOWN_FORMATS and keys of aiogoogle.validate.JSON_PYTHON_TYPE_MAPPING """
    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc["schemas"]

    def resolve(schema):
        if "$ref" in schema:
            return schemas[schema["$ref"]]
        else:
            return schema

    # schemas
    for _, schema in schemas.items():
        if "properties" in schema:  # 6 failures without this check
            for _, prop in schema["properties"].items():
                prop = resolve(prop)
                assert prop["type"] in JSON_PYTHON_TYPE_MAPPING
                if "format" in prop:
                    assert prop["format"] in KNOWN_FORMATS

    for method in methods_generator(name, version):
        if "parameters" in method:
            for _, param in method["parameters"].items():
                param = resolve(param)
                assert param["type"] in JSON_PYTHON_TYPE_MAPPING
                if "format" in param:
                    assert param["format"] in KNOWN_FORMATS


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_parameters_are_not_objects(
    open_discovery_document, name, version, methods_generator
):
    """ 
    I was curious whether global parameters might have identical names
    with Method.parameters.
    Fails if similarities found
    """
    for method in methods_generator(name, version):
        if method.parameters:
            for _, v in method.parameters.items():
                assert v.get("type") != "object"
                assert not v.get("properties")


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_schemas_consistency(open_discovery_document, name, version, methods_generator):
    """
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
        to perform the simplest of validations.
     """

    # Avoid infinite recursion e.g.
    # https://www.googleapis.com/discovery/v1/apis/bigquery/v2/rest / schemas / QueryParameterType schema
    schemas_checked = []

    def resolve(schema, schemas):
        """ Resolves schema if resolvable """
        if "$ref" in schema:
            schema = schemas[schema["$ref"]]
        return schema

    def validate(schema_name, schema, schemas):
        schema = resolve(schema, schemas)

        assert "type" in schema

        if schema["type"] == "object":
            if "properties" not in schema:
                ####################################################################################
                # Remove the following **line** for a proper test. This is just silencing the error
                if schema_name not in ["TokenPagination", "tokenPagination"]:
                    ####################################################################################
                    assert "additionalProperties" in schema
            else:
                for name, prop in schema["properties"].items():
                    if name not in schemas_checked:
                        schemas_checked.append(name)
                        validate(name, prop, schemas)
            if schema.get("additionalProperties"):
                schema = schema["additionalProperties"]
                if isinstance(schema, dict):
                    if "properties" not in schema:  # correct
                        if schema not in schemas_checked:
                            schemas_checked.append(schema)
                            validate("additionalProperties", schema, schemas)
                #    # If many additionalProperties, (it should only be one schema for all the additional props), iterate over them (Causes two more errors)
                #    else:
                #        for k,v in schema.items():
                #            # Might cause an infinite loop
                #            validate(k, v, schemas)
                # elif isinstance(prop, bool):
                #    pass
                # else:
                #    #raise TypeError(
                #    #    f'The following additionalProperty should be either a schema or bool not "{prop}"')
                #    pass
                #    #for _ in range(100000):
                #    #    print(prop)
        else:
            # all schemas/subschemas should eventually reach this point for testing
            if schema.get("pattern"):
                re.compile(schema["pattern"])

    disc_doc = open_discovery_document(name, version)
    schemas = disc_doc["schemas"]
    assert isinstance(schemas, dict)

    # Validate methods
    for method in methods_generator(name, version):
        for name, param in method.parameters.items():
            validate(name, param, schemas)

    # Validate schemas
    for name, schema in disc_doc["schemas"].items():
        if name not in schemas_checked:
            validate(name, schema, schemas)
