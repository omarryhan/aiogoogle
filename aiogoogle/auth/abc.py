from abc import ABC, abstractmethod
import inspect


class AbstractOAuth2Manager(ABC):

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
        return super(AbstractOAuth2Manager, cls).__new__(*args, **kwargs)

    @abstractmethod
    def authorize_request(self, request, creds):
        ''' Takes in a request and guarantees that it won't return a 401 by:
            - Refreshes the access token being handled if needed
            - Injects auth data to the request depending on the manager's protocol
        '''
        raise NotImplementedError

    @abstractmethod
    def is_expired(self, creds):
        raise NotImplementedError

    @abstractmethod
    async def refresh_creds(self, *creds, session_factory):
        ''' guarantees refreshed credentials or raises AuthError '''
        raise NotImplementedError

    @abstractmethod
    def build_oauth2_uri(self, client_creds, user_creds=None, state=None)-> (str, dict):
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

class AbstractAPIKeyManager(ABC):

    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(AbstractAPIKeyManager, predicate=inspect.iscoroutinefunction)

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f'{child_method} must be a coroutine')

        # Resume with normal behavior of a Python constructor
        return super(AbstractAPIKeyManager, cls).__new__(*args, **kwargs)

    @abstractmethod
    def authorize_request(self, request, creds):
        ''' Takes in a request and guarantees that it won't return a 401 by:
            - Refreshes the access token being handled if needed
            - Injects auth data to the request depending on the manager's protocol
        '''
        raise NotImplementedError