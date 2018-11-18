from abc import ABC, abstractproperty, abstractmethod, abstractclassmethod, abstractstaticmethod
import inspect


class AbstractSession(ABC):

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
        return super(AbstractSession, cls).__new__(cls, *args, **kwargs)

    @abstractmethod
    async def send(self, *requests, return_json_only=True, return_tasks=False):
        '''
        This method should accept
        args:
            *requests
        kwargs:
            return_json = True  # by default, if F
        
        pass
        '''
        NotImplemented