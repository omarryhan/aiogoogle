from jsonschema import ValidationError  # Import this to catch validation errors. Though I dont recommend it, you can simply set validate to False instead.

class AiogoogleError(Exception):
    pass

class HTTPError(AiogoogleError):
    pass

class AuthError(HTTPError):
    pass