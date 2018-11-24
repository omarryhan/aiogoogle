#from jsonschema import ValidationError  # Import this to catch validation errors. Though I dont recommend it, you can simply set validate to False instead.

class AiogoogleError(Exception):
    '''
    Base class for all of Aiogoogle's errors
    '''
    pass

class ValidationError(AiogoogleError):
    '''
    Raised when the validate flag is set true and validation error occurs
    '''
    pass

class HTTPError(AiogoogleError):
    '''
    HTTP related error
    '''
    pass

class AuthError(HTTPError):
    '''
    Authentication error. Inherits from HTTPError
    '''
    pass