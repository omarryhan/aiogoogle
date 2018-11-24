__all__ = [
    'ApiKey',
    'UserCreds',
    'ClientCreds'
]


from ..utils import _dict


class ApiKey(str):
    pass

class UserCreds(_dict):
    '''
    
    '''
    def __init__(
        self,
        access_token=None,
        refresh_token=None,
        expiry=None,
        created_at=None,
        id_token=None,
        scopes=None
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = expiry
        self.created_at = created_at
        self.id_token = id_token
        self.scopes = scopes
        # token_uri?

class ClientCreds(_dict):
    '''

    '''
    def __init__(self, client_id=None, client_secret=None, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
