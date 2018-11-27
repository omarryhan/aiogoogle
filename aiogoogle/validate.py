__all__ = [
    'validate',
    'resolve'
]

import datetime
import re

from .excs import ValidationError


#------- MAPPINGS -------#

TYPE_MAPPING = {
    'number': [float, int],
    'string': [str],
    'object': [dict],
    'array': [list],
    'boolean': [bool],
    'null': []
}

TYPE_FORMAT_MAPPING = {
    # Given this type, if None then don't check for additional "format" property in the schema
    'any': [],
    'array': [],
    'boolean': [],
    'integer': ['int32', 'unint32'],
    'number': ['double', 'float'],
    'object': [],
    'string': ['null', 'byte', 'date', 'date-time','int64','uint64']
}

def make_validation_error(checked_value, correct_criteria):
    return f"{checked_value} isn't valid. Expected a value that meets those criteria: {correct_criteria}"

#-------- VALIDATORS ---------#

# Type validators (JSON schema)

def any_validator(value):
    pass

def array_validator(value):
    if not isinstance(value, (list, set, tuple)):
        raise ValidationError(make_validation_error(value, 'List or Set or Tuple'))

def boolean_validator(value):
    if not isinstance(value, bool):
        raise ValidationError(make_validation_error(value, 'Boolean'))

def integer_validator(value):
    if not isinstance(value, int):
        raise ValidationError(make_validation_error(value, 'Integer'))

def number_valdator(value):
    if not isinstance(value, (int, float)):
        raise ValidationError(make_validation_error(value, 'Number'))

def object_validator(value):
    if not isinstance(value, (dict)):
        raise ValidationError(make_validation_error(value, 'Mappable object'))

def string_validator(value):
    if not isinstance(value, (str)):
        raise ValidationError(make_validation_error(value, 'String'))

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
    if not isinstance(value, datetime.date):
        raise ValidationError(make_validation_error(value, 'Python\'s datetime.date'))

def datetime_validator(value):
    if not isinstance(value, datetime.datetime):
        raise ValidationError(make_validation_error(value, 'Python\'s datetime.datetime'))

def null_validator(value):
    if value is not None:
        raise ValidationError(make_validation_error(value, 'None (null)'))

# Other Validators

def minimum_validator(value, minimum):
    if value < int(minimum):
        raise ValidationError(make_validation_error(value, f'Not less than {minimum}'))

def maximum_validator(value, maximum):
    if value > int(maximum):
        raise ValidationError(make_validation_error(value, f'Not less than {maximum}'))

#-- Executors ---------------------------

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

def resolve(name, schema, schemas):
    if name in schemas:
        pass

def validate(instance, schema, schemas):
    '''
    Arguments:

        Instance: Instance to validate

        schema: schema to validate instance against (top level schema)

        schemas: Full schamas dict to resolve refs if any
    '''
    # A simple instance validation module for Discovery schemas.
    # Unfrtunately, Google uses a slightly modified version of JSONschema draft3.
    # As a result, using an external library to validate Discovery schemas will raise lots of errors.
    # I tried to modify the popular: https://github.com/Julian/jsonschema to make it work with Google's version,
    # but it was just too complicated for the relatively simple task on our hands

    # Validate the following:
    # 1. DONE type (str) jsonschema types
    # 2. DONE format (str) discovery specific types https://developers.google.com/discovery/v1/type-format
    # 3. DONE minimum (str)
    # 4. DONE maximum (str)
    # 5. DONE pattern (str)

    # 6. required (bool)
    # 7. properties (dict): of nested schemas. Not to be confused with:
    #   I. "item" (a regular key in objects)
    #   II. "parameter" (isn't part of json schema, but part of method description)
    # 8. TODO: repeated: Whether this parameter may appear multiple times
    # 9. TODO: Support media upload/download validation without doing file io
    # 10.
    if not isinstance(schema, dict):
        raise TypeError('Schema should always be a dict')

    if isinstance(instance, dict):
        for k, v in instance.items():
            # Get next instance of schema
            if not isinstance(schema, dict):
                raise ValidationError(f'Invalid sub schema {schema}')
            corresponding_schema = schema.get(k)
            if not corresponding_schema:
                raise ValidationError(f'Couldn\'t find a schema for {instance}.')
            validate(v, corresponding_schema, schemas)
    elif isinstance(instance, (list, tuple)):
        pass
    else:
        validate_all(instance, schema)
