import warnings
from urllib.parse import urlencode

from jsonschema import validate as validate_, Draft3Validator, ValidationError as ValidationError_

from .excs import ValidationError
from .utils import _dict, _safe_getitem
from .excs import ValidationError
from .models import MediaDownload, MediaUpload, ResumableUpload, Request


# Those are the hard-coded kwargs in ResourceMethod.__call__
# They're used for testing whether those names will collide with any of the url parameters that are provided by any of the discovery docs.
# If collisions were to be found, that would mean that the user won't be able to pass a url_parameter that shares the same name with any of the PRESERVED_KEYWORDS.
PRESERVED_KEYWORDS = ['validate', 'data', 'json', 'upload_file', 'download_file', 'timeout']


class ResourceMethod:
    def __init__(self, name, method_specs, global_parameters, schemas, base_url, root_url, validate):
        self.name = name
        self._method_specs = method_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._root_url = root_url
        self._should_validate = validate

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

    def _validate(self, instance, schema):
        ref_resolved_schema = self._resolve_ref(schema, self._schemas)
        try:
            return validate_(instance, ref_resolved_schema, cls=Draft3Validator)
        except ValidationError_ as e:
            raise ValidationError(e)
    
    @staticmethod
    def _resolve_ref(schema: dict, schemas: dict):
        '''
        Args:

            schema: schema dict to be resolved (either from disc_doc['schemas']['schema'] or from disc_doc['resources']['resource']['methods']['method']['parameters']['parameter'])
            schemas: dict with many schema dicts
        
        Returns:

            resolved schema
        '''
        # This will mostly catch schema['request'] and schema['response']
        if schema is not None and schemas is not None:
            for k, v in schema.items():
                if isinstance(v, dict):
                    substitutable_ref = v.get('$ref')
                    if substitutable_ref:
                        ref = schemas[substitutable_ref]
                        for k1, v1 in ref.items():
                            v[k1] = v1
                        del v['$ref']

            # Do the same for schema['parameters'] if it exists
            if schema.get('parameters'):
                for k, v in schema['parameters'].items():
                    if isinstance(v, dict):
                        substitutable_ref = v.get('$ref')
                        if substitutable_ref:
                            v[substitutable_ref] = schemas[substitutable_ref]
                            del v['$ref']
        return schema

    def __call__(self, validate=None, data=None, json=None, upload_file=None, 
                download_file=None, timeout=None, **uri_params) -> Request:
        ''' 
        Builds a request

        validate: Overrides DiscoveryClient.validate if not None
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
        # Then, run the unit tests and monitor: tests.test_discovery_document.test_parameters_not_colliding_with_resource_method__call__ for failure

        # Assert timeout is int
        if timeout is not None:
            if not isinstance(timeout, int) or type(timeout) == bool:
                raise TypeError('Timeouts can only be ints or None')

        # Resolve validation status
        if not isinstance(validate, bool):
            validate = self._should_validate
        
        # Build full url minus query & fragment (i.e. uri)
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
            body = json if json is not None else data if data is not None else None
            if isinstance(body, dict):
                self._validate_body(body)

        # Process download_file
        if download_file:
            if validate is True:
                if getattr(self, 'supportsMediaDownload', None) is not True:
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
            method=self.httpMethod,
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
            for param_name in self.parameterOrder:
                try:
                    sorted_required_path_params[param_name] = uri_params.pop(param_name)
                except KeyError:
                    raise ValidationError(f'Missing URL path parameter: {param_name}')
            
            # Validate path params
            if validate is True:
                self._validate_url(sorted_required_path_params)

        # Build full path
            return self._base_url + self.path.format(**sorted_required_path_params)
        else:
            return self._base_url + self.path

    def _validate_url(self, sorted_required_path_params):
        for path_param_name, path_param_info in sorted_required_path_params.items():
            self._validate(path_param_info, self.parameters[path_param_name])  # instance, schema

    def _validate_body(self, req):
        request_schema = self._method_specs.get('request')
        if request_schema is not None:

            # If there's a reference resolve
            if '$ref' in request_schema:
                request_schema = self._schemas.get('$ref')
            
            # Check if request schema isn't not from the previous step
            if request_schema is not None:
                
                # Iterate over req and validate every param passed in req
                for k,v in req.items():

                    sub_schema_to_check_against = _safe_getitem(request_schema, 'properties', k)
                    
                    if sub_schema_to_check_against:

                        self._validate(v, sub_schema_to_check_against)

    def _build_upload_media(self, upload_file):
        # Check if method supports media upload
        # Will check wether validate is true or false
        if self._method_specs.get('supportsMediaUpload') is not True:
            raise ValidationError('upload_file was provided while method doesn\'t support media upload')
        
        # If resumable, create resumable object
        resumable = self._build_resumeable_media(upload_file) if _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'resumable') else None
        
        # Create MediaUpload object and pass it the resumable object we just created
        simple_upload_path = _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'simple', 'path') or ''
        if simple_upload_path:
            media_upload_url = self._root_url[:-1] + simple_upload_path
        else:
            media_upload_url = None 
        mime_range = _safe_getitem(self._method_specs, 'mediaUpload', 'accept')
        multipart = self.mediaUpload['protocols']['simple'].get('multipart', False)

        # Return
        return MediaUpload(upload_file, upload_path=media_upload_url, mime_range=mime_range, multipart=multipart, resumable=resumable)

    def _build_resumeable_media(self, upload_file):
            resumable_upload_path = _safe_getitem(self._method_specs, 'mediaUpload', 'protocols', 'resumable', 'path') or ''
            resumable_url = self._root_url[:-1] + resumable_upload_path
            multipart = self.mediaUpload['protocols']['resumable'].get('multipart', False)
            return ResumableUpload(upload_file, multipart=multipart, upload_path=resumable_url)

    def _validate_response(self, resp):
        pass

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.required_parameters) if self.required_parameters else 0

