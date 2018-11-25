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