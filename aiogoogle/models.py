from .utils import _dict


class Request:
    '''
    Request class for the whole library. Auth Managers, Resources and Sessions should all use this
    '''

    def __init__(self, *args, **kwargs):
        '''
        Parameters:

            base_url: API's base URL e.g. https://
            resource_path: path

        passes all the parameters passed to its appropriate setter instead of directly setting it for consistency
        '''
        pass

    @classmethod
    def batch_requests(cls, *requests):
        pass

class DiscoveryDocument(_dict):
    pass

class ResourceMethod:
    def __init__(self, *args, **kwargs):
        pass

class Resource:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, key):
        pass

class Resources:
    def __init__(self, discovery_document):
        self.discovery_document = DiscoveryDocument(discovery_document)

    def __getattr__(self, key):
        pass