from .abc import AbstractOAuth2Manager, AbstractAPIKeyManager
from .creds import UserCreds, ClientCreds
from .utils import _create_secret

from ..models import Request


# NOTE:
# - These are the default managers. They won't perform any file io.
# - If you want auth managers with file io capabilities, then you'll have to 
#   implement AbstractAuthManager's interface
# - Creds must always be an instance of dict


class Oauth2Manager(AbstractOAuth2Manager):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def authorize_request(self, request: Request, creds: dict) -> Request:
        if request.headers is None:
            request.headers = {}
        request.headers['Authorization'] = f'Bearer {creds["access_token"]}'
        return request

    def is_expired(self, creds: dict) -> bool:
        pass

    async def refresh_creds(self, *user_creds, client_creds=None) -> dict:

        # If no user creds where provided, refresh client creds via client credentials flow
        if not user_creds:
            return await self._refresh_client_creds(client_creds)

        # Else, refresh user credentials via authorization code flow
        else:
            return await self._refresh_user_creds(user_creds, client_creds)


    async def _refresh_user_creds(self, user_creds, client_creds) -> dict:
        pass

    async def _refresh_client_creds(self, client_creds) -> dict:
        pass

    def build_uri(self, client_creds, user_creds=UserCreds(), state=_create_secret(32)) -> (str, dict):
        ''' 
        First step of OAuth2 authoriztion code flow

            Parameters:

                client_creds: An instance of ClientCreds
                user_creds: An instance of UserCreds (Needed to store parameter:state)
                state: A csrf token. Leaving it empty will create a random secret

            Function:

                1. Check state
                2. Creates an oauth URI

            Returns: 
                1. oauth_uri
                2. instance of user_creds (with state in it)

            e.g.

                uri, user_creds = build_oauth2_uri()
        '''
        pass

    async def build_client_creds(self, client_creds) -> dict:
        '''
        Performs OAuth2 client credentials flow
        
        Parameters:

            client_creds: Client creds dict. Should have a client_id and client_secret

        Returns:

            client_creds: Returns the client_creds dict you pass + an access token item
        '''
        pass

    async def build_user_creds(self, grant, client_creds, user_creds, verify_state=True) -> dict:
        '''
        Second step of Oauth2 authrization code flow

        Parameters:

            grant: aka "code". The code received at your redirect URI
            user_creds: 
                Instance of UserCreds
                This will be used for verifying the state. (A CSRF token)
                It will then be populated with user's new access token, expires_in etc..

        Returns:

            An instance of UserCreds
        '''
        pass

class ApiKeyManager(AbstractAPIKeyManager):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def authorize_request(self, request, creds) -> Request:
        if request.headers is None:
            request.headers = {}
        request.headers['Authorization'] = f'Bearer {creds["access_token"]}'
        return request

class ServiceAccountManager:

    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def authorize_request(self, creds):
        raise NotImplementedError

    def is_expired(self, creds):
        raise NotImplementedError

    async def refresh_creds(self, creds):
        raise NotImplementedError
 