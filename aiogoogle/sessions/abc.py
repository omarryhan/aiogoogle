from abc import ABC, abstractproperty, abstractmethod, abstractclassmethod, abstractstaticmethod
import inspect


class AbstractResponse(ABC):

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

    @abstractproperty
    def url(self):
        pass

    @abstractproperty
    def status_code(self):
        pass

    @abstractmethod
    async def json(self):
        pass

    @abstractmethod
    async def content(self):
        ''' Should return an object that implements AbstractContent '''
        pass

    @abstractmethod
    async def 

    async def 

    @abstractmethod
    def raise_for_status(self):
        '''
        A method that should raise a google_async.excs.HTTPError for status codes that are >= 400.
        Preferably this should pass constructor the original error raised
        '''
        pass

class AbstractContent(ABC):
    @abstractmethod
    def iter_chunked(self):
        '''
        This method should return an iterable to be used as such:

            for data in AbstractResponse.AbstractContent
        '''
        

class AbstractSession(ABC):

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
    async def send(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        '''
        This method should accept
        args:
            *requests
        kwargs:
            return_json = True  # by default, if F
        
        pass
        '''
        raise NotImplementedError