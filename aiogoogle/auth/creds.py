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
        expires_in (int): seconds till expiry from creation
        scopes (list): list of scopes owned by access token
        
        id_token (str): OpenID token
        id_token_jwt (str): OpenID token JWT
        
        token_type (str): Bearer
        token_uri (str): "https://accounts.google.com/o/oauth2/token"
        token_info_uri (str): "https://www.googleapis.com/oauth2/v3/tokeninfo",
        revoke_uri (str): "https://accounts.google.com/o/oauth2/revoke"
        
    '''
    def __init__(
        self,
        access_token=None,
        refresh_token=None,
        expires_in=None,
        scopes=None,
        
        id_token=None,
        id_token_jwt=None,
        
        token_type=None,
        token_uri=None,
        token_info_uri=None,
        revoke_uri=None
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.scopes = scopes
        
        self.id_token = id_token
        self.id_token_jwt = id_token_jwt
        
        self.token_type = token_type
        self.token_uri = token_uri
        self.token_info_uri = token_info_uri
        self.revoke_uri = revoke_uri

class ClientCreds(_dict):
    '''
    OAuth2 Client Credentials Dictionary

    Examples:

        Scopes:



    Arguments:

        client_id (str): OAuth2 client ID
        client_secret (str): OAuth2 client secret
        scopes (list): List of scopes that this client should request from resource server
        redirect_uri (str): client's redirect uri
    '''
    def __init__(self, client_id=None, client_secret=None, scopes=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.redirect_uri = redirect_uri
