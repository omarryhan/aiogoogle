from .utils import _dict

class Request:
    '''
    Request class for the whole library. Auth Managers, Resources and Sessions should all use this
    '''

    def __init__(
        self, method=None, url=None, headers=None, json=None, data=None,
        chunked_upload=False, chunked_download=False, upload_file_name=None, download_file_name=None):
        '''
        Parameters:

            method: HTTP method as a string (upper case) e.g. 'GET'
            url: full url as a string. e.g. 'https://example.com/api/v1/resource?filter=filter#something
            headers: headers as a dict
            
            HTTP BODY:
            Only pass one of the below:
              
              - json: json as a dict
              - data: www-url-form-encoded form as a dict/ bytes/ text/ 
              - upload_file_name: see below

            chunked_request: Whether you want to stream content of the request as chunks
            chunked_response: Whether you want to stream the content of the response as chunks
            upload_file_name:
              - Full file path for the file you want to upload
            download_file_name:
              - Be careful as this will overwrite one of your files if a file with identical name was found
        '''
        self.method = method
        self.url = url
        self.headers = headers
        self.json = json
        self.data = data
        self.chunked_upload = chunked_upload
        self.chunked_download = chunked_download
        self.upload_file_name = upload_file_name
        self.download_file_name = download_file_name

    @classmethod
    def batch_requests(cls, *requests):
        pass

class ResourceMethod:
    def __init__(self, name, method_specs, global_parameters=None, schema=None):
        self.name = name
        self._method_specs = method_specs
        self._global_parameters = global_parameters
        self._schema = schema

    @property
    def description(self):
        return self._method_specs.get('description')
    
    @property
    def scopes(self):
        return self._method_specs.get('scopes')

    def __call__(self, **kwargs):
        ''' builds a request '''
        pass

class Resource:
    def __init__(self, name, resource, global_parameters=None, schema=None):
        self.name = name
        self._resource = resource
        self._global_parameters = global_parameters
        self._schema = schema

    @property
    def methods(self) -> [str, str]:
        # Some resources have nested resources, ergo the need for "{}"
        methods_ = self._resource.get('methods')
        return [k for k,v in methods_.items()] if methods_ else []

    @property
    def resources(self) -> [str, str]:
        '''
        Checks if there's any nested resources in the discovery document

        e.g.:
        resources:
            a_resource:
                resources:
                    a_resource
                        a_method
                        another_method
                    a_resource
                        a_method
                        another_method
                    a_resource
                        a_method
                        another_method
            a_resource
                a_method
        '''

        if self._resource.get('resources'):
            return [k for k,v in self._resource.get('resources').items()]
        else:
            return []
        

    def __getattr__(self, method_or_resource):
        '''
        Will first check for nested resources then will check for methods on main resource
        '''
        # 1. Search in nested resources
        if method_or_resource in self.resources:
            return Resource(
                name=method_or_resource,
                resource=self._resource['resources'][method_or_resource],
                global_parameters=self._global_parameters,
                schema=self._schema
            )
        # 2. Must be a method
        elif method_or_resource in self.methods:
            return ResourceMethod(
                name=method_or_resource,
                method_specs=self._resource['methods'][method_or_resource],
                global_parameters=self._global_parameters,
                schema=self._schema
            )
        else:
            raise AttributeError(f'Resource doesn\'nt have a method or resource called: {method_or_resource}.\n\nAvailable methods are: {self.available_methods} and available resources are: {self.nested_resources}')

class Resources:
    def __init__(self, discovery_document, schema, auth, global_parameters):
        self.discovery_document = discovery_document

        # Set reusable parts to this object in order to minimize memory consumption
        self._schema = schema
        self._auth = auth
        self._global_parameters = global_parameters
        self._resources = discovery_document.get('resources')

    def __getattr__(self, resource) -> Resource:
        # If resource is found in the "resources" in the discovery document
        if resource in self._resources:
            return Resource(name=resource, resource=self._resources[resource], global_parameters=self._global_parameters, schema=self._schema)
        else:
            documentation_link = self.discovery_document.get('documentationLink') or 'https://developers.google.com/'
            raise AttributeError(f"Resource doesn't exist. Check: {documentation_link} for more info")
             