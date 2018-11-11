from abc import ABC, abstractmethod


class AbstractAuthManager(ABC):

    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(AbstractResponse, predicate=inspect.iscoroutinefunction)

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f'{child_method} must be a coroutine')

        # Resume with normal behavior of a Python constructor
        return super(AbstractResponse, cls).__new__(cls, *args, **kwargs)

    @abstractmethod
    def authorize_request(self, request, creds):
        ''' Takes in a request and guarantees that it won't return a 401 by:
            - Refreshes the access token being handled if needed
            - Injects auth data to the request depending on the manager's protocol
        '''
        pass

    @abstractmethod
    def is_expired(self, creds):
        pass

    @abstractmethod
    async def refresh_creds(self, *creds, session_factory):
        ''' guarantees refreshed credentials or raises AuthError '''
        pass