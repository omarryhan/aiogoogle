__all__ = [
    'GoogleAPI',
    'Resource',
    'Method'
]

import warnings
from urllib.parse import urlencode
from functools import wraps

from .excs import ValidationError
from .utils import _dict, _safe_getitem, _toggle2x_dashed_params
from .excs import ValidationError
from .models import MediaDownload, MediaUpload, ResumableUpload, Request
from .validate import validate as validate__


# These are the hard-coded kwargs in Method.__call__
# They're used for testing whether those names will collide with any of the url parameters that are provided by any of the discovery docs.
# If collisions were to be found, that would mean that the user won't be able to pass a url_parameter that shares the same name with any of the RESERVED_KEYWORDS.
RESERVED_KEYWORDS = ['validate', 'data', 'json', 'upload_file', 'download_file', 'timeout']

# From: https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/discovery.py
# Parameters accepted by the stack, but not visible via discovery.
STACK_QUERY_PARAMETERS = frozenset(['trace', 'pp', 'strict'])
STACK_QUERY_PARAMETER_DEFAULT_VALUE = {
    'type': 'string',
    'location': 'query',
}

# TODO: Add default media type
BODY_PARAMETER_DEFAULT_VALUE = {
    'description': 'The request body.',
    'type': 'object',
    'required': True,
}
MEDIA_BODY_PARAMETER_DEFAULT_VALUE = {
    'description': ('The filename of the media request body, or an instance '
                    'of a MediaUpload object.'),
    'type': 'string',
    'required': False,
}
MEDIA_MIME_TYPE_PARAMETER_DEFAULT_VALUE = {
    'description': ('The MIME type of the media request body, or an instance '
                    'of a MediaUpload object.'),
    'type': 'string',
    'required': False,
}


class Method:
    # TODO: Add defaults
    # TODO: Add enum and enum description properties both to docstring and __call__
    def __init__(self, name, method_specs, global_parameters, schemas, base_url, root_url, service_path, validate):
        # Replaces '-'s with '_'s and preserve old names to revert back to them after this method is called
        global_parameters = self._rm_dash_params(global_parameters)
        method_specs['parameters'] = self._rm_dash_params(method_specs.get('parameters'))

        self.name = name
        self._method_specs = method_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._root_url = root_url
        self._service_path = service_path
        self._should_validate = validate

        # TODO: add docstring to call here
        # self.__call__.__doc__ = 'wattt?'  # won't work
        # self.__call__.__doc__ = self.__call__.__doc__.format('watt')  # Won't work
        # global_function.__call__.__doc__ = 'wattt'  # won't work
        # global_function.__call__.__doc__ = fucntion.__call__.__doc__.format('watt')  # WILL work

#---- Change URL parameters with a "-" to "_" -----#

    def _rm_dash_params(self, param_set) -> dict:
        if param_set:
            for name, schema in param_set.items():
                if '-' in name:
                    new_name = name.replace('-', '_')
                    schema['orig_name'] = name
                    param_set[new_name] = schema
                    del param_set[name]
        return param_set

    def _add_dash_params(self, param_set) -> dict:
        if param_set:
            # list() forces the creation of a new copy in memory
            # to avoid having the dict size changing during iteration
            for name, schema in list(param_set.items()):
                if 'orig_name' in schema:
                    param_set[schema['orig_name']] = schema
                    del param_set[name]
        return param_set

    def _add_dash_user_uri_params(self, uri_params):
        for k,v in uri_params.items():
            if '_' in k:
                if k in self.parameters:
                    if 'orig_name' in self.parameters[k]:
                        uri_params[self.parameters[k]['orig_name']] = v
                        del uri_params[k]
        return uri_params

#---- / Change URL parameters with a "-" to "_" -----#

    @property
    def request(self) -> dict:
        ''' Returns expected request body '''
        body = self['request']
        if body.get('$ref'):
            return self._schemas.get(body['$ref'])
        else:
            return body

    @property
    def response(self) -> dict:
        ''' Retruns expected response body '''
        body = self['response']
        if body.get('$ref'):
            return self._schemas.get(body['$ref'])
        else:
            return body

    @property
    def parameters(self) -> dict:
        if not self._global_parameters and not self['parameters']:
            return {}
        elif not self._global_parameters:
            return self['parameters']
        elif not self['parameters']:
            return self._global_parameters
        else:
            return {**self['parameters'], **self._global_parameters}

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
    
    def __getitem__(self, key):
        '''

        Possible additional attributes from the discovery doc

            Arguments:

                description: method description

                scopes: method's required scopes

                supportsMediaDownload

                supportsMediaUpload
        '''
        return self._method_specs.get(key)

    def _validate(self, instance, schema):
        return validate__(instance, schema, self._schemas)
        #try:
        #    return validate_(instance, schema, cls=Draft3Validator)
        #except ValidationError_ as e:
        #    raise ValidationError(e)

    @_toggle2x_dashed_params
    def __call__(self, validate=None, data=None, json=None, upload_file=None, 
                download_file=None, timeout=None, **uri_params) -> Request:
        ''' 
        Builds a request

        validate: Overrides Aiogoogle.validate if not None
        json: Json body
        data: Data body (Bytes, text, www-url-form-encoded and others)
        upload_file: file to upload
        download_file: file to download to
        timeout: total timeout
        **uri_params: (path and query) (required and optional) parameters
        '''
        # If collisions are found between the 'key' of **uri_params and explicit kwargs e.g. data, json etc., then 
        # priority will be given to explicit kwargs. With that said, it's not likely there will be any.
        # If you want to double check if there are any collisions,
        # you can append the API name and version you're using to tests.globals.SOME_APIS (only if they don't exist, otherwise, you shouldn't worry about collisions)
        # Then, run the unit tests and monitor: tests.test_discovery_document.test_parameters_not_colliding_with_google_api__call__ for failure

        #
        # NOTE: Use '_' instead of '-' when passing uri parameters that have a '-' in their names
        #

        # Assert timeout is int
        if timeout is not None:
            if not isinstance(timeout, int) or type(timeout) == bool:
                raise TypeError('Timeouts can only be ints or None')

        # Resolve validation status
        if not isinstance(validate, bool):
            validate = self._should_validate
        
        # Build full url minus query & fragment
        url = self._build_url(uri_params=uri_params, validate=validate)

        # Filter out query parameters from all uri_params that were passed to this method
        passed_query_params = {param_name: param_info for param_name, param_info in uri_params.items() if param_name in self.query_parameters}

        # Ensure all required query parameteters were passed
        for param in self.required_query_parameters:
            if param not in passed_query_params:
                raise ValidationError(f'Missing query parameter: \"{param}\"')

        # Validate url query params
        if validate is True:
            if passed_query_params:
                for param_name, passed_param in passed_query_params.items():
                    self._validate(passed_param, self.parameters[param_name])
        
        # Join query params
        if passed_query_params:
            uri = url + '?' + urlencode(passed_query_params)
        else:
            uri = url

        # Pop uri_params consumed
        for param_name, _ in passed_query_params.items():
            del uri_params[param_name]

        # Warn if not all uri_params were consumed/popped
        if uri_params:  # should be empty by now
            warnings.warn('Parameters {} were not used and are being discarded.'
                          ' Check if they\'re valid parameters'.format(str(uri_params)))

        # Ensure only one param for http req body.
        if json and data:
            raise TypeError('Pass either json or data for the body of the request, not both.'
                            '\nThis is similar to the "body" argument in google-python-client'
                            '\nThis will validate agains the $request key in this method\'s '
                            'discovery document')  # This raises a TypeError instead of a ValidationError because 
                                                   # it will probably make your session raise an error if it passes.

        # Validate body
        if validate is True:
            body = json if json is not None else data if data is not None else None  # json or data or None
            if isinstance(body, dict):
                self._validate_body(body)

        # Process download_file
        if download_file:
            if validate is True:
                if self.__getitem__('supportsMediaDownload') is not True:
                    raise ValidationError('download_file was provided while method doesn\'t support media download')
            media_download = MediaDownload(download_file)
        else:
            media_download = None

        # Process upload_file
        if upload_file:
            media_upload = self._build_upload_media(upload_file)
        else:
            media_upload = None

        return Request(
            method=self['httpMethod'],
            url=uri,
            data=data,
            json=json,
            timeout=timeout,
            media_download=media_download,
            media_upload=media_upload
        )

    def _build_url(self, uri_params, validate):
        if self.path_parameters:
            # sort path params as sepcified in method_specs.parameterOrder
            sorted_required_path_params = {}  # Dict order is guaranteed (by insertion) as of Python 3.6+
            for param_name in self['parameterOrder']:
                try:
                    sorted_required_path_params[param_name] = uri_params.pop(param_name)
                except KeyError:
                    raise ValidationError(f'Missing URL path parameter: {param_name}')

            # Validate path params
            if validate is True:
                self._validate_url(sorted_required_path_params)

        # Build full path
            return self._base_url + self['path'].format(**sorted_required_path_params)
        else:
            return self._base_url + self['path']

    def _validate_url(self, sorted_required_path_params):
        for path_param_name, path_param_info in sorted_required_path_params.items():
            self._validate(path_param_info, self.parameters[path_param_name])  # instance, schema

    def _validate_body(self, req):
        request_schema = self._method_specs.get('request')
        if request_schema is not None:
            if '$ref' in request_schema:
                request_schema = self._schemas[request_schema['$ref']]
            self._validate(req, request_schema)
        else:
            raise ValidationError('Body should\'ve been validated, but wasn\'t because a schema body wasn\'nt found')

    def _build_upload_media(self, upload_file):
        # Will check wether validate is true or false
        if self['supportsMediaUpload'] is not True:
            raise ValidationError('upload_file was provided while method doesn\'t support media upload')
        
        # If resumable, create resumable object
        resumable = self._build_resumeable_media(upload_file) if _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'resumable') else None
        
        # Create MediaUpload object and pass it the resumable object we just created
        simple_upload_path = _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'simple', 'path')
        media_upload_url = self._root_url[:-1] + simple_upload_path
        mime_range = _safe_getitem(self._method_specs, 'mediaUpload', 'accept')
        multipart = self['mediaUpload']['protocols']['simple'].get('multipart', False)

        # Return
        return MediaUpload(upload_file, upload_path=media_upload_url, mime_range=mime_range, multipart=multipart, resumable=resumable)

    def _build_resumeable_media(self, upload_file):
            resumable_upload_path = _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'resumable', 'path')
            resumable_url = self._root_url[:-1] + resumable_upload_path
            multipart = self['mediaUpload']['protocols']['resumable'].get('multipart', False)
            return ResumableUpload(upload_file, multipart=multipart, upload_path=resumable_url)

    def _validate_response(self, resp):
        ''' Maybe add this as a callback that a session should call after it fetches the content of the response? '''
        pass

    def __contains__(self, item):
        return item in self.parameters

    def __str__(self):
        return self['id']

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.required_parameters) if self.required_parameters else 0


class Resource:
    def __init__(self, name, resource_specs, global_parameters, schemas, base_url, root_url, service_path, validate):
        self.name = name
        self._resource_specs = resource_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._root_url = root_url
        self._service_path = service_path
        self._validate = validate  

    @property
    def methods(self) -> [str, str]:
        return [k for k,v in self['methods'].items()] if self['methods'] else []

    @property
    def resources(self) -> [str, str]:
        '''
        Checks if there's any nested resources in the discovery document
        '''
        return [k for k,v in self['resources'].items()] if self['resources'] else []

    def __str__(self):
        return self.name + ' resource @ ' + self._base_url

    def __repr__(self):
        return self.__str__()

    def __call__(self):
        raise TypeError('Only methods are callables, not resources.'
                        ' e.g. client.resources.user.list() NOT client.resources.user().list()')

    def __len__(self):
        return len(self.methods)

    def __contains__(self, item):
        return ((item in self.methods) or (item in self.resources))

    def __getitem__(self, k):
        return self._resource_specs.get(k)

    def __getattr__(self, method_or_resource):
        '''
        Will first check for nested resources then will check for methods on main resource
        '''
        # 1. Search in nested resources
        if method_or_resource in self.resources:
            return Resource(
                name=method_or_resource,
                resource_specs=self['resources'][method_or_resource],
                global_parameters=self._global_parameters,
                schemas=self._schemas,
                base_url=self._base_url,
                root_url=self._root_url,
                service_path=self._service_path,
                validate=self._validate
            )
        # 2. Search in methods
        elif method_or_resource in self.methods:
            return Method(
                name=method_or_resource,
                method_specs=self['methods'][method_or_resource],
                global_parameters=self._global_parameters,
                schemas=self._schemas,
                base_url=self._base_url,
                root_url=self._root_url,
                service_path=self._service_path,
                validate=self._validate
            )
        else:
            raise AttributeError(f'''Resource doesn\'t have a method or resource called:
                                    \"{method_or_resource}\".\n\nAvailable methods are:
                                    {self.methods} and available resources are: {self.resources}
                                ''')

class GoogleAPI:
    def __init__(self, discovery_document, validate=True):
        self.discovery_document = self._add_extra_params(discovery_document)
        self._validate = validate

    def _add_extra_params(self, discovery_document):
        ''' Adds extra parameters that aren't mentioned in the discovery docuemnt '''
        extra_params = {param: STACK_QUERY_PARAMETER_DEFAULT_VALUE for param in STACK_QUERY_PARAMETERS}
        if discovery_document.get('parameters'):
            discovery_document['parameters'] = {**discovery_document['parameters'], **extra_params}
        else:
            discovery_document['parameters'] = extra_params
        return discovery_document

    def __getattr__(self, resource) -> Resource:
        # If resource is found in the "resources" in the discovery document
        if resource in self['resources']:
            return Resource(
                name=resource,
                resource_specs=self['resources'][resource],
                global_parameters=self['parameters'],
                schemas=self['schemas'] or {},  # josnschema validator will fail if schemas isn't a dict
                base_url= self['baseUrl'],
                root_url=self['rootUrl'],
                service_path=self['servicePath'],
                validate=self._validate
            )
        else:
            documentation_link = self.discovery_document.get('documentationLink') or 'https://developers.google.com/'
            raise AttributeError(f"Resource doesn't exist. Check: {documentation_link} for more info")

    def __getitem__(self, k):
        return self.discovery_document.get(k)

    def __contains__(self, item):
        return item in self['resources']
    
    def __repr__(self):
        available_resources_names = [k for k,v in self['resources'].items()] if self['resources'] else []
        client_info = self.discovery_document['name'] + '-' + self.discovery_document['version']
        return client_info + '\n\n' + 'Available resources: ' +'\n' + str(available_resources_names)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self['resources']) if self['resources'] else 0

    def __call__(self):
        raise TypeError('Only methods are callables, not resources.'
                        ' e.g. client.resources.user.list() NOT client.resources().user.list()')
