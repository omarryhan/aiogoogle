class AiogoogleError(Exception):
    pass

class ValidationError(AiogoogleError):
    '''
    Raised when the validate flag is set true and validation error occurs
    '''
    pass

class HTTPError(AiogoogleError):
    pass

class AuthError(HTTPError):
    pass