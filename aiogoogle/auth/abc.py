from abc import ABC, abstractmethod
import inspect

from ..models import Request


class AbstractOAuth2Manager(ABC):
    '''
    OAuth2 manager that only supports:
        
        - Authorization Code Flow (https://tools.ietf.org/html/rfc6749#section-1.3.1)
    
    * For a flow similar to the Client Credentials Flow (https://tools.ietf.org/html/rfc6749#section-1.3.4) use an api_key
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
        '''
        Arguments:

            session_factory:

                A session object that can be called with an asynchronous context manager
        
        Returns:

            None
        '''
        raise NotImplementedError

    @abstractmethod
    def authorize(self, request, creds) -> Request:
        ''' 
        Arguments:

            Request:

                Request to authorize

            Creds:

                user_creds to refresh with

        Returns:

            Request:

                Request with valid OAuth2 authorizaion header
        '''
        raise NotImplementedError

    @abstractmethod
    def is_expired(self, user_creds):
        '''
        Checks if user_creds are expired

        Arguments:
        
            user_creds (dict):

                user_creds dict with ['expiry'] and ['created_at'] items

        Returns:

            (bool)

        '''
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, user_creds, client_creds):
        '''
        Refreshes user_creds
        
        Arguments:

            user_creds:

                dict with ['refresh_token'] item

            
        '''
        raise NotImplementedError

    @abstractmethod
    def build_auth_uri(self, client_creds, user_creds=None, state=None)-> (str, dict):
        ''' 
        First step of OAuth2 authoriztion code flow

            Arguments:

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
        raise NotImplementedError

    @abstractmethod
    async def build_user_creds(self, grant, client_creds, user_creds, verify_state=True) -> dict:
        '''
        Second step of Oauth2 authrization code flow

        Parameters:

            grant (str):
            
                - Aka: "code". 
                - The code received at your redirect URI

            client_creds (dict):

                - Dict with client_id, client_secret items

            user_creds (dict):

                - Instance of UserCreds
                - This will be used for verifying the state. (A CSRF token)
                - It will then be populated with user's new access token, expires_in etc..

            verify_state:

                - Whether or not to verify state 

        Returns:

            An dict representing credentials of a user.
            Credentials will contain the following items

                - access_token
                - refresh_token
                - expiry  i.e. "expires in"
                - created_at (datetime json_format)
                - id_token
                - scopes

        '''
        raise NotImplementedError

class AbstractAPIKeyManager(ABC):

    @abstractmethod
    def authorize(self, request, api_key):
        '''
        Adds API key as a url query parameter

        Arguments:

            request: request instance defined in aiogoogle.models

            api_key: api_key from Google's dev console. aka: Developer's Key

        Returns:

            Same request object passed with the developer's key in its url arguments

        '''
        raise NotImplementedError