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

class ResourceMethod:
    def __init__(self, method_specs, global_parameters, schema):
        self._method_specs = method_specs
        self._global_parameters = global_parameters
        self._schema = schema

    def __call__(self, **kwargs):
        ''' builds a request '''
        pass

class Resource:
    def __init__(self, specs, global_parameters=None, schema=None):
        self._specs = specs
        self._global_parameters = global_parameters
        self._schema = schema

    def __getattr__(self, method):
        # If method requested is found in the "methods" section in resources
        if method in self._specs['methods']:

            # Create a RequestMethod object
            setattr(self, method, RequestMethod())

class Resources:
    def __init__(self, discovery_document, schema, auth, global_parameters):
        self.discovery_document = discovery_document

        # Set reusable parts to this object in order to minimize memory consumption
        self._schema = schema
        self._auth = auth
        self._global_parameters = global_parameters
        self._resources = discovery_document.get('resources')

    def __getattr__(self, resource):
        # If resource is found in the "resources" in the discovery document
        if resource in self._resources:

            # 1. Instantiate a resource object with
            #   1. Specs of the resource being queried
            #   2. Global parameters
            #   3. Full schema section
            # 2. Set it to object
            setattr(self, resource, Resource(specs=self._resources[resource], global_parameters=self._global_parameters, schema=self._schema)) 
            
            # 3. Return
            return self.__getattr__(self, resource)
        else:
            raise AttributeError("Resource doesn't exist. Check: {self.discovery_document['documentationLink'] for more info}")
             