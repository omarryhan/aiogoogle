'''
A simple instance validation module for Discovery schemas.
Unfrtunately, Google uses a slightly modified version of JSONschema draft3.
As a result, using an external library to validate Discovery schemas will raise lots of errors.
I tried to modify the popular: https://github.com/Julian/jsonschema to make it work with Google's version,
but it was just too complicated for the relatively simple task on our hands

Validate the following:
1. DONE type (str) jsonschema types
2. DONE format (str) discovery specific types https://developers.google.com/discovery/v1/type-format
3. DONE minimum (str)
4. DONE maximum (str)
5. DONE pattern (str)

6. required (bool)
7. properties (dict): of nested schemas. Not to be confused with:
  I. "item" (a regular key in objects)
  II. "parameter" (isn't part of json schema, but part of method description)
8. TODO: repeated: Whether this parameter may appear multiple times
9. TODO: Support media upload/download validation without doing file io
10.
'''

__all__ = [
    'validate',
]

import datetime
import warnings
import re

from .excs import ValidationError


def make_validation_error(checked_value, correct_criteria):
    return f"{checked_value} isn't valid. Expected a value that meets those criteria: {correct_criteria}"

#------- MAPPINGS -------#

JSON_PYTHON_TYPE_MAPPING = {
    'number': (float, int),
    'integer': (int),
    'string': (str),
    'object': (dict),
    'array': (list, set, tuple),
    'boolean': (bool),
    'null': (),  # Not used
    'any': (float, int, str, dict, list, set, tuple, bool, datetime.datetime, datetime.date)
}

TYPE_FORMAT_MAPPING = {
    # Given this type, if None then don't check for additional "format" property in the schema, else, format might be any of the mapped values
    # Those are kept here for reference. They aren't used by any validator, instead validators check directly if there's any format requirements
    'any': [],
    'array': [],
    'boolean': [],
    'integer': ['int32', 'unint32'],
    'number': ['double', 'float'],
    'object': [],
    'string': ['null', 'byte', 'date', 'date-time','int64','uint64']
}

#-------- VALIDATORS ---------#

# Type validators (JSON schema)

def any_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['any']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def array_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['array']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def boolean_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['boolean']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def integer_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['integer']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def number_valdator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['number']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def object_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['object']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

def string_validator(value):
    req_types = JSON_PYTHON_TYPE_MAPPING['string']
    if not isinstance(value, req_types):
        raise ValidationError(make_validation_error(value, str(req_types)))

# Format validators (Discovery Specific)  https://developers.google.com/discovery/v1/type-format

def int32_validator(value):
    if (value > 2147483648) or (value < -2147483648) :
        raise ValidationError(make_validation_error(value, 'Integer between -2147483648 and 2147483648'))

def uint32_validator(value):
    if (value < 0) or (value > 4294967295):
        raise ValidationError(make_validation_error(value, 'Integer between 0 and 4294967295'))

def int64_validator(value):
    if (value > 9223372036854775807) or (value < -9223372036854775807):
        raise ValidationError(make_validation_error(value, 'Integer between -9,223,372,036,854,775,807 and -9,223,372,036,854,775,807'))

def uint64_validator(value):
    if (value > 9223372036854775807*2) or (value < 0):
        raise ValidationError(make_validation_error(value, 'Integer between 0 and 9,223,372,036,854,775,807 * 2'))

def double_validator(value):
    if not isinstance(value, float):
        raise ValidationError(make_validation_error(value, 'Double type'))

def float_validator(value):
    if not isinstance(value, float):
        raise ValidationError(make_validation_error(value, 'Float type'))

def byte_validator(value):
    if not isinstance(value, bytes):
        raise ValidationError(make_validation_error(value, 'Bytes type'))

def date_validator(value):
    msg = make_validation_error(value, 'JSON date value. Hint: use datetime.date.isoformat(), instead of datetime.date')
    try:
        pvalue = datetime.date.fromisoformat(value)
    except:
        raise ValidationError(msg)
    if not isinstance(pvalue, datetime.date):
        raise ValidationError(msg)

def datetime_validator(value):
    msg = make_validation_error(value, 'JSON date value. Hint: use datetime.datetime.isoformat(), instead of datetime.datetime')
    try:
        pvalue = datetime.datetime.fromisoformat(value)
    except:
        raise ValidationError(msg)
    if not isinstance(pvalue, datetime.datetime):
        raise ValidationError(msg)

def null_validator(value):
    if value != 'null':
        raise ValidationError(make_validation_error(value, "'null' NOT None"))

# Other Validators

def minimum_validator(value, minimum):
    if value < int(minimum):
        raise ValidationError(make_validation_error(value, f'Not less than {minimum}'))

def maximum_validator(value, maximum):
    if value > int(maximum):
        raise ValidationError(make_validation_error(value, f'Not less than {maximum}'))

#-- Sub validators ---------------------------

def validate_type(instance, schema):
    type_validator_name = schema['type']
    type_validator = globals()[type_validator_name + '_validator']
    type_validator(instance)

def validate_format(instance, schema):
    if schema.get('format'):
        format_validator_name = schema['format']
        if format_validator_name == 'date-time':
            format_validator_name = 'datetime'
        format_validator = globals()[format_validator_name + '_validator']
        format_validator(instance)

def validate_range(instance, schema):
    if schema.get('minimum'):
        minimum_validator(instance, schema['minimum'])
    elif schema.get('maximum'):
        maximum_validator(instance, schema['maximum'])

def validate_pattern(instance, schema):
    pattern = schema.get('pattern')
    if pattern is not None:
        match = re.match(pattern, instance)
        if match is None:
            raise ValidationError(instance, f'Match this pattern: {pattern}')

#-- Main Validator ---------------

def validate_all(instance, schema):
    validate_type(instance, schema)
    validate_format(instance, schema)
    validate_range(instance, schema)
    validate_pattern(instance, schema)

#-- API --------------------

def validate(instance, schema, schemas=None):
    '''
    Arguments:

        Instance: Instance to validate

        schema: schema to validate instance against

        schemas: Full schamas dict to resolve refs if any
    '''
    def resolve(schema):
        '''
        Resolves schema from schemas
        if no $ref was found, returns original schema
        '''
        if schemas is None:
            raise ValidationError(f"Attempted to resolve {k}, but no schema was found to resolve from")
        if '$ref' in schema:
            try:
                schema = schemas[schema['$ref']]
            except KeyError:
                raise ValidationError(f"Attempted to resolve {schema['$ref']}, but no result was found.")
        return schema

    # Check schema and schemas are dicts
    if not isinstance(schema, dict):
        raise TypeError('Schema must be a dict')
    if schemas is not None:
        if not isinstance(schemas, dict):
            raise TypeError('Schemas must be a dict')

    # Preliminary resolvement
    schema = resolve(schema)
    
    # If object (Dict): iterate over each entry and recursively validate
    if schema['type'] == 'object':        
        # Validate instance is an object
        object_validator(instance)
        # Raise warnings on passed dict keys that aren't mentioned in the schema
        for k, _ in instance.items():
            if k not in schema['properties']:
                warnings.warn(f"Item {k} was passed, but not mentioned in the following schema {schema.get('id')}.\n\n It will probably be discarded by the API you're using")
        # Validate
        for k,v in schema['properties'].items():
            # Check if there's a ref to resolve
            v = resolve(v)
            # Check if instance has the property, if not, check if it's required
            if k not in instance:
                if v.get('required') is True:
                    raise ValidationError(f"Instance {k} is required")
            else:
                validate(instance[k], v, schemas)

    # If array (list) iterate over each item and recursively validate
    elif schema['type'] == 'array':
        # Validate instance is an array
        array_validator(instance)
        schema = resolve(schema['items'])
        # Check if instance has the property, if not, check if it's required
        for item in instance:
            validate(item, schema, schemas)

    # Else we reached the lowest level of a schema, validate 
    else:
        validate_all(instance, schema)
