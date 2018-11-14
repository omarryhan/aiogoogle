from .abc import AbstractAuthManager
from .creds import UserCreds, ClientCreds
from .utils import _create_secret

from ..models import Request


class Oauth2Manager:

    __metaclass__ = AbstractAuthManager

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def authorize_request(self, request: Request, creds) -> Request:
        pass

    def is_expired(self, creds) -> bool:
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

    def build_oauth2_uri(self, client_creds, user_creds=UserCreds(), state=_create_secret(32)) -> str:
        ''' 
        First step of OAuth2 authoriztion code flow

            Parameters:

                client_creds: An instance of ClientCreds
                user_creds: An instance of UserCreds (Needed to store parameter:state)
                state: A csrf token. Leaving it empty will create a random secret

            Function:

                1. Check state
                2. Sends 
        '''
        pass

    async def build_user_creds_from_grant(self, grant, client_creds, user_creds, verify_state=True) -> dict:
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

class ApiKeyManager:

    __metaclass__ = AbstractAuthManager

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def authorize_request(self, request, creds) -> Request:
        pass

    def is_expired(self, api_key) -> bool:
        return False

    async def refresh_creds(self, api_key: str) -> str:
        return api_key

class ServiceAccountManager:

    __metaclass__ = AbstractAuthManager

    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def authorize_request(self, creds):
        raise NotImplementedError

    def is_expired(self, creds):
        raise NotImplementedError

    async def refresh_creds(self, creds):
        raise NotImplementedError
 