from pprint import pprint
import json

from .utils import _dict
from .models import Request
from .resource import Resources
from .auth.managers import Oauth2Manager, ServiceAccountManager, ApiKeyManager
from .sessions.aiohttp_session import AiohttpSession


DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'


class DiscoveryClient:
    def __init__(self, session_factory=AiohttpSession, api_key=None, user_creds=None, client_creds=None,
                 service_account_creds=None, discovery_document={}, validate=True):
        '''
        Arguments:

            session_factory:

                - A factory that produces session object conforming to aiogoogle.sessions.abc.AbstractSession interface.

                    - You can choose from the few implementations of AbstractSession in the aiogoogle.sessions module

                    - In case you want to instantiate a custom session with initial parameters, you can either:

                        - Pass an anonymous factory. e.g.: `lambda: Session(your_custom_kwarg=True)`
                          aiogoogle will not pass any arguments to the session factory.

                        - Implement your own session factory

            api_key: 
            
                - Google API key

            user_creds: 
            
                - User credentials dict for the oauth2 manager

            client_creds:
                
                - Client credentials dict for the oauth2 manager

            service_account_creds:
            
                - Service account credentials dict for the service account manager

            discovery_document (dict):

                - Optional
                - You can download and set a discovery doc after instantiating a DiscoveryClient by calling self.discover()

            validate:

                - whether or not to validate input when calling methods
        '''

        self.session_factory = session_factory
        self.active_session = None
        self.validate = validate
        self.discovery_document = discovery_document

        # Keys
        self.api_key = api_key
        self.user_creds = user_creds
        self.client_creds = client_creds
        self.service_account_creds = service_account_creds

        # Auth managers
        self.api_key_manager = ApiKeyManager(self.session_factory)
        self.service_account_manager = ServiceAccountManager(self.session_factory)
        self.oauth2_manager = Oauth2Manager(self.session_factory)

    #-------- Discovery Document ---------#

    @property
    def discovery_document(self):
        return self._discovery_document

    @discovery_document.setter
    def discovery_document(self, discovery_document):
        self._discovery_document = discovery_document

        # Make a gateway object that will be responsible for creating requests that access resources from google's apis.
        self.resources = Resources(self._discovery_document, validate=self.validate)

    async def _download_discovery_document(self, api_name, api_version):
        url = DISCOVERY_URL.format(api_name=api_name, api_version=api_version)
        request = Request(method='GET', url=url)
        
        if self.active_session is None:
            async with self:
                discovery_docuemnt = await self.as_anon(request)
        else:
            discovery_docuemnt = await self.as_anon(request)
        return discovery_docuemnt

    async def discover(self, api_name, api_version):
        ''' 
        
        Donwloads and sets a discovery document from: 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'
        Makes this a object client to {api_name} + " " + {api_version}
        
        Arguments:

            api_name: API name to discover. e.g.: "youtube"
            
            api_version: API version to discover e.g.: "v3" NOT 3

        '''

        self.discovery_document = await self._download_discovery_document(api_name, api_version)

    #-------- Send Requests ----------#

    async def as_client(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends requests on behalf of self.client_creds (OAuth2)
        
        Arguments:

            *requests:

                Requests from client.resources.resource.method()

            timeout:

                Total timeout for all the requests being sent

            full_resp:

                If True, returns full HTTP response object instead of returning it's content
        '''
        # Refresh credentials
        self.client_creds = self.oauth2_manager.refresh_creds(
            client_creds=self.client_creds
        )

        # Authorized requests
        authorized_requests = [self.oauth2_manager.authorize_request(request, self.client_creds) for request in requests]

        # Send authorized requests
        return await self.active_session.send(*authorized_requests, timeout=timeout, return_full_http_response=full_resp)


    async def as_user(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends requests on behalf of self.user_creds (OAuth2)
        
        Arguments:

            *requests:

                Requests from client.resources.resource.method()

            timeout:

                Total timeout for all the requests being sent

            full_resp:

                If True, returns full HTTP response object instead of returning it's content
        '''
        # Refresh credentials
        self.user_creds = self.oauth2_manager.refresh_creds(
            self.user_creds,
            client_creds=self.client_creds
        )

        # Authroize requests
        authorized_requests = [self.oauth2_manager.authorize_request(request, self.user_creds) for request in requests]

        # Send authorized requests
        return await self.active_session.send(*authorized_requests, timeout=timeout, return_full_http_response=full_resp)

    async def as_service_account(self, *requests, timeout=None, full_resp=False):
        '''
        NotImplented
        Sends requests on behalf og self.service_account_creds
        '''
        raise NotImplementedError

    async def as_api(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends requests on behalf of self.api_key (OAuth2)
        
        Arguments:

            *requests:

                Requests from client.resources.resource.method()

            timeout:

                Total timeout for all the requests being sent

            full_resp:

                If True, returns full HTTP response object instead of returning it's content
        '''

        # Authorize requests
        authorized_requests = [self.api_key_manager.authorize_request(request, self.api_key) for request in requests]

        # Send authorized requests
        return await self.active_session.send(*authorized_requests, timeout=timeout, return_full_http_response=full_resp)

    async def as_anon(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends an unauthorized request
        
        Arguments:

            *requests:

                Requests from client.resources.resource.method()

            timeout:

                Total timeout for all the requests being sent

            full_resp:

                If True, returns full HTTP response object instead of returning it's content
        '''
        return await self.active_session.send(*requests, timeout=timeout, return_full_http_response=full_resp)

    def user_authorized_for_method(self, method, user_creds=None) -> bool:
        '''
        Checks if oauth2 user_creds object has sufficient scopes for a method call
        However, Doesn't check whether creds are refreshed or valid. As this is done automatically before each request.


        Arguments:

            Method: 
            
                - Method to be checked
                
                e.g.:

                    Correct:
                 
                        youtube = DiscoveryClient(discovery_document=ytb_doc)
                        is_authorized = youtube.user_authorized_for_resource(
                            youtube.resources.video.list
                        )
                    
                    NOT correct:

                        is_authorized = youtube.user_authorized_for_resource(
                            youtube.resources.video.list()
                        )

                    AND NOT correct:

                        is_authorized = youtube.user_authorized_for_resource(
                            youtube.resources.videos
                        )

        '''
        if user_creds is None:
            user_creds = self.user_creds
        method_scopes = getattr(method, 'scopes', []) 
        if not method_scopes:
            return True
        
        if not isinstance(user_creds['scopes'], (list, set, tuple)):
            raise TypeError('Scopes should be an instance of list, set or tuple')
        
        if set(method_scopes).issubset(
            set(user_creds['scopes'])
        ):
            return True
        else:
            return False

    def __getattr__(self, value):
        try:
            return self.discovery_document[value]
        except KeyError:
            raise AttributeError(f"Attribute/key \"{value}\" were not found in client and not in discovery document")

    async def __aenter__(self):
        self.active_session = await self.session_factory().__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.active_session.__aexit__(*args, **kwargs)

    def __repr__(self):
        return self.title or (self.name + '-' + self.version)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        try:
            return len(self.resources)
        except AttributeError:
            return 0
