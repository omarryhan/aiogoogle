__all__ = ['AbstractSession']


from abc import ABC, abstractproperty, abstractmethod, abstractclassmethod, abstractstaticmethod
import inspect


class AbstractSession(ABC):
    '''
    Object with `` async def send`` method. Should represent an HTTP session that has an asynchronous context manager
    '''

    def __new__(cls, *args, **kwargs):
        # Get all coros of this the abstract class
        parent_abstract_coros = inspect.getmembers(AbstractSession, predicate=inspect.iscoroutinefunction)

        # Ensure all relevant child methods are implemented as coros
        for coro in parent_abstract_coros:
            coro_name = coro[0]
            child_method = getattr(cls, coro_name)
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError(f'{child_method} must be a coroutine')

        # Resume with normal behavior of a Python constructor
        return super(AbstractSession, cls).__new__(cls)

    @abstractmethod
    async def send(self, *requests, timeout=None,  return_full_http_response=False):
        '''
        Main entry point of session. Takes requests, sends them, returns response contents or full http responses as defined in models
        
        Arguments:
            
            *requests (aiogoogle.models.Request):

                Request objects from aiogoogle.models
            
            timeout (int):

                Total timeout for *requests

            return_full_http_response (bool)

        Returns:

            aiogoogle.models.Response

        Raises:

            aiogoogle.excs.HTTPError

        '''
        NotImplemented