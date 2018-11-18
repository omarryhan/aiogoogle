from urllib.parse import urlencode
import warnings

from jsonschema import validate, RefResolver, Draft3Validator, validators

from .utils import _dict, _safe_getitem


PRESERVED_KEYWORDS = ['validate', 'data', 'json', 'upload_file', 'download_file', 'timeout']


class ResumableUpload:
    ''' Works in conjustion with media upload '''
    def __init__(self, file_path, multipart=None, upload_path=None):
        '''
        file_path: Full path of the file to be uploaded
        upload_path: The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        multipart: True if this endpoint supports upload multipart media.
        '''
        self.file_path = file_path
        self.upload_path = upload_path
        self.multipart = multipart

class MediaUpload:
    def __init__(self, file_path, upload_path=None, mime_range=None, max_size=None, multipart=False, resumable=None):
        '''
        file_path: Full path of the file to be uploaded
        upload_path: The URI path to be used for upload. Should be used in conjunction with the rootURL property at the API-level.
        mime_range: list of MIME Media Ranges for acceptable media uploads to this method.
        max_size: Maximum size of a media upload, such as "1MB", "2GB" or "3TB".
        multipart: True if this endpoint supports upload multipart media.
        resumable: A ResumableUpload object
        '''
        self.file_path = file_path
        self.upload_path = upload_path
        self.mime_range = mime_range
        self.max_size = max_size
        self.multipart = multipart
        self.resumable = resumable

class MediaDownload:
    def __init__(self, file_path):
        '''
        file_path: Full path of the file to be downloaded
        '''
        self.file_path = file_path

class Request:
    '''
    Request class for the whole library. Auth Managers, Resources and Sessions should all use this
    '''

    def __init__(
        self, method=None, url=None, headers=None, json=None, data=None,
        media_upload=None, media_download=None, timeout=None):
        '''
        Parameters:

            method: HTTP method as a string (upper case) e.g. 'GET'
            url: full url as a string. e.g. 'https://example.com/api/v1/resource?filter=filter#something
            headers: headers as a dict
            
            HTTP BODY (Only pass one of the following):
              
              - json: json as a dict
              - data: www-url-form-encoded form as a dict/ bytes/ text/ 

            media_download: MediaDownload object
            media_upload: MediaUpload object
            timeout: total request timeout in seconds

        '''
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data
        self.json = json
        self.media_upload = media_upload
        self.media_download = media_download
        self.timeout = timeout


    @classmethod
    def batch_requests(cls, *requests):
        # https://developers.google.com/discovery/v1/batch
        raise NotImplementedError


class ResourceMethod:
    def __init__(self, name, method_specs, global_parameters, schemas, base_url, validate):
        self.name = name
        self._method_specs = method_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._validate = validate

    
    @property
    def _validator(self):
        _ref_resolver = RefResolver.from_schema(self._schemas)
        _draft_validator = Draft3Validator(self._schemas, resolver=_ref_resolver)
        return lambda instance, schema: _draft_validator.validate(instance, schema)
        #return lambda instance, schema: validate(instance, schema, cls=_draft_validator)

    @property
    def parameters(self) -> dict:
        if not self._global_parameters and not self._method_specs.get('parameters'):
            return {}
        elif not self._global_parameters:
            return self._method_specs['parameters']
        elif not self._method_specs.get('parameters'):
            return self._global_parameters
        else:
            return {**self._method_specs['parameters'], **self._global_parameters}

    @property
    def optional_parameters(self) -> [str, str]:
        return [parameter_name for parameter_name, parameter_info in self.parameters.items() if parameter_info.get('required') is not True] if self.parameters else []

    @property
    def required_parameters(self) -> [str, str]:
        return [parameter_name for parameter_name, parameter_info in self.parameters.items() if parameter_info.get('required') is True] if self.parameters else []
    
    @property
    def path_parameters(self) -> [str, str]:
        return [param_name for param_name, param_info in self.parameters.items() if param_info.get('location') == 'path'] if self.parameters else []

    @property
    def query_parameters(self) -> [str, str]:
        return [param_name for param_name, param_info in self.parameters.items() if param_info.get('location') == 'query'] if self.parameters else []

    @property
    def required_query_parameters(self) -> [str, str]:
        return [param_name for param_name in self.query_parameters if param_name in self.required_parameters] if self.query_parameters else []

    @property
    def optional_query_parameters(self) -> [str, str]:
        return [param_name for param_name in self.query_parameters if param_name in self.optional_parameters] if self.query_parameters else []
    
    def __getattr__(self, value):
        '''
        returns info from discovery document. 
        where self._method_specs == discovery_document['resources']['resource']['method'] '''
        try:
            return self._method_specs[value]
        except KeyError:
            raise AttributeError(f'{self.name} method doesn\'t have a {value} attribute.')

    def __call__(self, validate=None, data=None, json=None, upload_file=None, 
                download_file=None, timeout=None, **url_params) -> Request:
        ''' 
        Builds a request

        validate: Overrides DiscoveryClient.validate if not None
        json: Json body
        data: Data body (Bytes, text, www-url-form-encoded and others)
        upload_file: file to upload
        download_file: file to download to
        timeout: total timeout
        **url_params: (path and query) (required and optional) parameters
        '''
        # if collisions were found between **url_params and explicit kwargs e.g. data, json etc., then 
        # priority will be given to explicit kwargs
        
        # Resolve validation status
        if not isinstance(validate, bool):
            validate = self._validate

        # Ensure only one param for http req body.
        if json and data:
            raise TypeError('Pass either json or data for the body of the request, not both.'
                            '\nThis is similar to the "body" argument in google-python-client'
                            '\nThis will validate agains the $request key in this method\'s '
                            'discovery document')
        
        # Build full url minus query & fragment
        if self.path_parameters:
            # sort path params as sepcified in method_specs.parameterOrder
            sorted_required_path_params = {}  # Dict order is guaranteed (by insertion) as of Python 3.6+
            for param_name in self.parameterOrder:
                try:
                    sorted_required_path_params[param_name] = url_params.pop(param_name)
                except KeyError:
                    raise KeyError(f'Missing URL path parameter: {param_name}')
            # Validate path params
            if validate is True:
                for path_param_name, path_param_info in sorted_required_path_params.items():
                    self._validator(path_param_info, self.parameters[path_param_name])  # instance, schema
        # Build full path
            url_path = self.path.format(**sorted_required_path_params)
        else:
            url_path = self.path

        # Validate body
        body = json or data
        if validate is True:
            if body is not None:
                self._validator(body, self.request)

        # Filter out query parameters from url_params that were passed to this method
        passed_query_params = {param_name: param_info for param_name, param_info in url_params.items() if param_name in self.query_parameters}
        # pop url params consumes
        for param_name, _ in passed_query_params.items():
            del url_params[param_name]
        # Ensure all required query parameteters were passed
        for param in self.required_query_parameters:
            if param not in passed_query_params:
                raise TypeError(f'Missing query parameter: \"{param}\"')

        # Validate url query params
        if validate is True:
            if passed_query_params:
                for param_name, passed_param in passed_query_params.items():
                    self._validator(passed_param, self.parameters[param_name])

        # Make full path
        if url_path:
            full_path = self._base_url + url_path
        else:
            full_path = self._base_url

        # Join query params
        if passed_query_params:
            full_url = full_path + '?' + urlencode(passed_query_params)
        else:
            full_url = full_path

        # Warn if not all url_params were consumed/popped
        if url_params:
            warnings.warn('Parameters {} were not used and are being discarded.'
                          ' Check if they\'re valid parameters'.format(str(url_params)))

        # Process download_file
        if download_file:
            if getattr(self, 'supportsMediaDownload', None) is not True:
                raise ValueError('download_file was provided while method doesn\'t support media download')
            media_download = MediaDownload(download_file)
        else:
            media_download = None

        # Process upload file
        if upload_file:

            # Check if method supports media upload
            if getattr(self, 'supportsMediaUpload') is not True:
                raise ValueError('upload_file was provided while method doesn\'t support media upload')
            
            # If resumable, create resumable object
            resumable = None
            if _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'resumable'):
                resumable_url = self._base_url + self.mediaUpload['protocols']['resumable']['path']
                multipart = self.mediaUpload['protocols']['resumable'].get('multipart', False)
                resumable = ResumableUpload(upload_file, multipart=multipart, upload_path=resumable_url)
            
            # Create MediaUpload object
            
            media_upload_url = self._base_url + _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'simple', 'path')
            mime_range = _safe_getitem(self._method_specs, 'mediaUpload', 'accept')
            media_upload = MediaUpload(upload_file, upload_path=media_upload_url, mime_range=mime_range, resumable=resumable)
        else:
            media_upload = None

        return Request(
            method=self.httpMethod,
            url=full_url,
            data=data,
            json=json,
            timeout=timeout,
            media_download=media_download,
            media_upload=media_upload
        )

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.required_parameters) if self.required_parameters else 0


class Resource:
    def __init__(self, name, resource_specs, global_parameters, schemas, base_url, validate):
        self.name = name
        self._resource_specs = resource_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._validate = validate

    @property
    def methods(self) -> [str, str]:
        # Some resources have nested resources, ergo the need for "{}"
        methods_ = self._resource_specs.get('methods')
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
                        methods:
                            a_method
                            another_method
                        resources:
                            a_resource
                                methods:...
                                resources:...
                    a_resource
                        methods:
                            a_method
                            another_method
            a_resource
                a_method
        methods:
            a_method
        '''
        resources_ = self._resource_specs.get('resources')
        return [k for k,v in resources_.items()] if resources_ else []

    def __str__(self):
        return self.name + ' resource @ ' + self._base_url

    def __repr__(self):
        return self.__str__()

    def __call__(self):
        raise TypeError('Only methods of resources are callables, not resources.'
                        ' e.g. client.resources.user.list() NOT client.resources.user().list()')

    def __len__(self):
        return len(self.methods)

    def __getattr__(self, method_or_resource):
        '''
        Will first check for nested resources then will check for methods on main resource
        '''
        # 1. Search in nested resources
        if method_or_resource in self.resources:
            return Resource(
                name=method_or_resource,
                resource_specs=self._resource_specs['resources'][method_or_resource],
                global_parameters=self._global_parameters,
                schemas=self._schemas,
                base_url=self._base_url,
                validate=self._validate
            )
        # 2. Search in methods
        elif method_or_resource in self.methods:
            return ResourceMethod(
                name=method_or_resource,
                method_specs=self._resource_specs['methods'][method_or_resource],
                global_parameters=self._global_parameters,
                schemas=self._schemas,
                base_url=self._base_url,
                validate=self._validate
            )
        else:
            raise AttributeError(f'Resource doesn\'t have a method or resource called: \"{method_or_resource}\".\n\nAvailable methods are: {self.methods} and available resources are: {self.resources}')

class Resources:
    def __init__(self, discovery_document, validate):
        self.discovery_document = discovery_document

        # Set reusable parts to this object in order to minimize memory consumption
        self._schemas = discovery_document.get('schemas', {})  # josnschema validator will fail if schemas isn't a dict
        self._auth = discovery_document.get('auth')
        self._global_parameters = discovery_document.get('parameters')
        self._resources_specs = discovery_document.get('resources')
        self._base_url = discovery_document.get('baseUrl')
        self._validate = validate

    def __getattr__(self, resource) -> Resource:
        # If resource is found in the "resources" in the discovery document
        if resource in self._resources_specs:
            return Resource(
                name=resource,
                resource_specs=self._resources_specs[resource],
                global_parameters=self._global_parameters,
                schemas=self._schemas,
                base_url= self._base_url,
                validate=self._validate
            )
        else:
            documentation_link = self.discovery_document.get('documentationLink') or 'https://developers.google.com/'
            raise AttributeError(f"Resource doesn't exist. Check: {documentation_link} for more info")
    
    def __repr__(self):
        available_resources_names = [k for k,v in self._resources_specs.items()] if self._resources_specs else []
        client_info = self.discovery_document['name'] + '-' + self.discovery_document['version']
        return client_info + '\n' + 'Available resources: ' +'\n' + str(available_resources_names)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self._resources_specs) if self._resources_specs else 0

    def __call__(self):
        raise TypeError('Only methods of resources are callables, not resources.'
                        ' e.g. client.resources.user.list() NOT client.resources().user.list()')