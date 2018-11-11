from functools import wraps
        
def refresh_creds(creds_name, manager_name):
    '''
    1. Sends the creds specified to be refreshed if expired
    2. Sets tham back to the instance that the method is bound to
    '''
    def outer_wrapper(f):
        @wraps(f)
        async def wrapper(self, *requests, **kwargs):
            manager = getattr(self, manager_name)
            creds = getattr(self, creds_name)
            
            # refreshes creds with manager
            if manager.is_expired(creds):
                creds = manager.refresh(creds)
            
            return f(self, *requests, **kwargs) 
        return wrapper
    return outer_wrapper

def authorize_requests(creds_name, manager_name):
    '''
    1. Sniffs all the requests passed to a wrapped method
    2. Sends the requests to the specified auth manager
    3. Manager adds authorization headers and returns authorized requests
    4. The wrapper then injects them back to the wrapped method
    '''
    def outer_wrapper(f):
        @wraps(f)
        async def wrapper(self, *requests, **kwargs):
            manager = getattr(self, manager_name)
            creds = getattr(self, creds_name)

            # authorizes requests with manager
            authorized_requests = [manager.authorize_request(request, creds) for request in requests]

            return f(self, *authorized_requests, **kwargs)
        return wrapper
    return outer_wrapper