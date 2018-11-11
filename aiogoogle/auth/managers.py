from .abc import AbstractAuthManager
from .creds import UserCreds, ClientCreds


#class AuthManager:
#
#    __metaclass__ = AbstractAuthManager
#        
#    def authorize_request(self, *args, **kwargs):
#        ''' Takes in a request and guarantees that it won't return a 401 by:
#            - Refreshes the access token being handled if needed
#            - Injects auth data to the request depending on the manager's protocol
#        '''
#        raise NotImplementedError
#
#    def is_expired(self, *args, **kwargs):
#        raise NotImplementedError
#
#    async def refresh_creds(self, *args, **kwargs):
#        ''' guarantees refreshed credentials or raises AuthError '''
#        raise NotImplementedError

class Oauth2Manager:

    __metaclass__ = AbstractAuthManager

    # https://github.com/jpadilla/pyjwt
    def authorize_request(self, request, creds):
        pass

    def is_expired(self, creds):
        pass

    async def refresh_creds(self, *user_creds, client_creds, session_factory):

        # If no user creds where provided, refresh client creds via client credentials flow
        if not user_creds:
            return await self._refresh_client_creds(client_creds, session_factory)

        # Else, refresh user credentials via authorization code flow
        else:
            return await self._refresh_user_creds(*user_creds, client_creds, session_factory)


    async def _refresh_user_creds(self, *user_creds, client_creds, session_factory):
        

    async def _refresh_client_creds(self, client_creds, session_factory):
        pass

    def build_oauth2_uri(self, client_creds, user_creds=UserCreds(), state=None):
        ''' 
        First step of OAuth2 authoriztion code flow

            Parameters:

                client_creds: An instance of ClientCreds
                user_creds: An instance of UserCreds (Needed to store parameter:state)
                state: A csrf token. Leaving it empty will create a random secret
        '''
        pass

    async def build_user_creds_from_grant(self, grant, client_creds, user_creds, session_factory, verify_state=True):
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

    def authorize_request(self, request, creds):
        pass

    def is_expired(self, creds):
        return False

    async def refresh_creds(self, *creds, session_factory):
        return creds

class ServiceAccountManager(AuthManager):

    __metaclass__ = AbstractAuthManager
    
    def authorize_request(self, creds):
        raise NotImplementedError

    def is_expired(self, creds):
        raise NotImplementedError

    async def refresh_creds(self, *creds, session_factory):
        raise NotImplementedError
 