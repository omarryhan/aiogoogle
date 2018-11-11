class GoogleAsyncError(Exception):
    pass

class HTTPError(GoogleAsyncError):
    pass

class AuthError(HTTPError):
    pass