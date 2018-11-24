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
    OAuth2 User Credentials Dictionary

    Arguments:

        access_token (str): Access Token
        refresh_token (str): Refresh Token
        expiry (int): seconds till expiry from creation
        created_at (str): Date time this object was created at - JSON datetime string
        id_token (str): Open ID token
        scopes (list): list of scopes owned by access token
        state (str): OAuth2 state token 
    '''
    def __init__(
        self,
        access_token=None,
        refresh_token=None,
        expiry=None,
        created_at=None,
        id_token=None,
        scopes=None,
        state=None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry = expiry
        self.created_at = created_at
        self.id_token = id_token
        self.scopes = scopes
        self.state = state
        # token_uri?

class ClientCreds(_dict):
    '''
    OAuth2 Client Credentials Dictionary

    Arguments:

        client_id (str): OAuth2 client ID
        client_secret (str): OAuth2 client secret
        scopes (list): List of scopes that this client should request from resource server
    '''
    def __init__(self, client_id=None, client_secret=None, scopes=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
