from .method import ResourceMethod

class Resource:
    def __init__(self, name, resource_specs, global_parameters, schemas, base_url, root_url, validate):
        self.name = name
        self._resource_specs = resource_specs
        self._global_parameters = global_parameters
        self._schemas = schemas
        self._base_url = base_url
        self._root_url = root_url
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
                root_url=self._root_url,
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
                root_url=self._root_url,
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
        self._root_url = discovery_document.get('rootUrl')
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
                root_url=self._root_url,
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