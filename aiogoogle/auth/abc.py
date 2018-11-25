from abc import ABC, abstractmethod
import inspect

from ..models import Request


class AbstractOAuth2Manager(ABC):
    '''
    OAuth2 manager that only supports Authorization Code Flow (https://tools.ietf.org/html/rfc6749#section-1.3.1)

    Arguments:

        session_factory (aiogoogle.sessions.AbstractSession): A session implementation
    
    Note:
    
        For a flow similar to Client Credentials Flow (https://tools.ietf.org/html/rfc6749#section-1.3.4) use an ``api_key``
    '''

    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(AbstractOAuth2Manager, predicate=inspect.iscoroutinefunction)

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f'{child_method} must be a coroutine')

        # Resume with normal behavior of a Python constructor
        return super(AbstractOAuth2Manager, cls).__new__(cls)

    @abstractmethod
    def __init__(self, session_factory):
        raise NotImplementedError

    @abstractmethod
    def authorize(self, request, creds) -> Request:
        '''
        Adds OAuth2 authorization headers to requests given user creds

        Arguments:

            request (aiogoogle.models.Request):

                Request to authorize

            creds (aiogoogle.auth.creds.UserCreds):

                user_creds to refresh with

        Returns:

            aiogoogle.models.Request: Request with OAuth2 authorization header
        '''
        raise NotImplementedError

    @abstractmethod
    def is_expired(self, user_creds):
        '''
        Checks if user_creds expired

        Arguments:
        
            user_creds (aiogoogle.auth.creds.UserCreds): User Credentials

        Returns:

            bool:

        '''
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, user_creds, client_creds):
        '''
        Refreshes user_creds
        
        Arguments:

            user_creds (aiogoogle.auth.creds.UserCreds): User Credentials

            client_creds (aiogoogle.auth.creds.ClientCreds): Client Credentials

        Returns:

            aiogoogle.creds.UserCreds: Refreshed user credentials

        Raises:

            aiogoogle.excs.AuthError: Auth Error
        '''
        raise NotImplementedError

    @abstractmethod
    def build_auth_uri(self, client_creds, state=None)-> (str, dict):
        ''' 
        First step of OAuth2 authoriztion code flow.

        Creates an OAuth2 authorization URI.

        If no state is passed, this method will generate and add a secret token to ``user_creds['state']``.
        
        e.g. ::

            auth_uri, user_creds = self.build_auth_uri(client_creds, state='A CSRF token')
    

        Arguments:

            client_creds (aiogoogle.auth.creds.ClientCreds): Client Creds
            
            state (str): A CSRF token

        Returns:

            (str, aiogoogle.auth.creds.UserCreds): If no state was passed, A new state item will be found in ``UserCreds``

        '''
        raise NotImplementedError

    @abstractmethod
    async def build_user_creds(self, grant, client_creds, user_creds=None, state=None):
        '''
        Second step of Oauth2 authrization code flow

        Creates a User Creds object with access and refresh token

        User Credentials dict return should contain these items:

            - access_token
            - refresh_token
            - expiry  i.e. "expires in"
            - created_at (datetime json_format)
            - id_token
            - scopes

        Arguments:

            grant (str):
            
                - Aka: "code". 
                - The code received at your redirect URI

            client_creds (aiogoogle.auth.creds.ClientCreds):

                - Dict with client_id, client_secret items

            user_creds (aiogoogle.auth.creds.UserCreds):

                - Optional
                - You should prefferably pass this method the UserCreds instance returned from``build_auth_uri`` method
                - This will be used for verifying the state. (A CSRF token)
                - a "state" should be found in user_creds
                - It will then be populated with user's new access token, expires_in etc..

            state (str):

                - Should be the state query argument found in the user's OAuth2 callback.
                - This keyword argument must be used with the user_creds kwarg.

        Returns:

            aiogoogle.auth.creds.UserCreds: User Credentials

        Raises:

            aiogoogle.excs.AuthError: Auth Error
        '''
        raise NotImplementedError

class AbstractAPIKeyManager(ABC):

    @abstractmethod
    def authorize(self, request, api_key):
        '''
        Adds API Key authorization query argument to URL of a request given an API key

        Arguments:

            request (aiogoogle.models.Request):

                Request to authorize

            creds (aiogoogle.auth.creds.ApiKey):

                ApiKey to refresh with

        Returns:

            aiogoogle.models.Request: Request with API key in URL
        '''
        raise NotImplementedError
