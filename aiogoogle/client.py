from pprint import pprint
import json

from .utils import _dict
from .models import Request, Resources
from .auth.managers import Oauth2Manager, ServiceAccountManager, ApiKeyManager
from .sessions.aiohttp_session import AiohttpSession


DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'


class DiscoveryClient:
    def __init__(self, session_factory=AiohttpSession, api_key=None, user_creds=None, client_creds=None,
                 service_account_creds=None, discovery_document={}, validate=True):
        '''
        Parameters:

            session_factory:

                - A factory that produces sessions. (Or just a callable object)
                    - You can choose from the many implementations of AbstractSession in the sessions module
                    - In case you want to instantiate a custom session with initial parameters, you can pass an anonymous factory. e.g.: `lambda: Session(default_timeout=7)`
                - Session should implement google_async.sessions.abc.AbstractSession

            api_key: 
            
                - Google API key

            user_creds: 
            
                - User credentials dict for the oauth2 manager

            client_creds:
                
                - Client credentials dict for the oauth2 manager

            service_account_creds:
            
                - Service account credentials dict for the service account manager

            discovery_document:

                - Optional
                - Should be a dict.
                - You can download and set a discovery doc after instantiating a DiscoveryClient by calling self.discover()

            validate:

                - whether or not to validate input when calling methods of resources
        '''

        self.session_factory = session_factory
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
        return await self.send_unauthorized(request)

    async def discover(self, api_name, api_version):
        ''' Downloads discovery document and sets it to self '''
        self.discovery_document = await self._download_discovery_document(api_name, api_version)

    #-------- Send Requests ----------#

    async def send_as_client(self, *requests, return_full_http_response=False):
        ''' 
        Sends requests on behalf of self.client_creds
        Uses OAuth2
        '''
        # Refresh credentials
        self.client_creds = self.oauth2_manager.refresh_creds(
            client_creds=self.client_creds
        )

        # Authorized requests
        authorized_requests = [self.oauth2_manager.authorize_request(request, self.client_creds) for request in requests]

        # Send authorized requests
        async with self.session_factory() as session:
            responses = await session.send(*authorized_requests, return_full_http_response=return_full_http_response)
        return responses


    async def send_as_user(self, *requests, return_full_http_response=False):
        '''
        Sends requests on behalf of self.user_creds
        Uses OAuth2
        '''
        # Refresh credentials
        self.user_creds = self.oauth2_manager.refresh_creds(
            self.user_creds,
            client_creds=self.client_creds
        )

        # Authroize requests
        authorized_requests = [self.oauth2_manager.authorize_request(request, self.user_creds) for request in requests]

        # Send authorized requests
        async with self.session_factory() as session:
            responses = await session.send(*authorized_requests, return_full_http_response=return_full_http_response)
        return responses

    async def send_as_service_account(self, *requests, return_full_http_response=False):
        '''
        Sends requests on behalf og self.service_account_creds
        '''
        raise NotImplementedError

    async def send_as_api(self, *requests, return_full_http_response=False):
        '''
        Sends requests on behalf of the owner of self.api_key
        '''

        # Authorize requests
        authorized_requests = [self.api_key_manager.authorize_request(request, self.api_key) for request in requests]

        # Send authorized requests
        async with self.session_factory() as session:
            responses = await session.send(*authorized_requests, return_full_http_response=return_full_http_response)
        return responses

    async def send_unauthorized(self, *requests, return_full_http_response=False):
        '''
        Sends unauthorized requests
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_full_http_response=return_full_http_response)
        return responses

    def user_authorized_for_method(self, resource_method, user_creds=None) -> bool:
        '''
            - Checks if oauth2 user creds have sufficient scopes for a method of a resource i.e. ResourceMethod
        However, Doesn't check whether creds are refreshed or valid. As this is done automatically before each request

        e.g. input:
                youtube = DiscoveryClient(discovery_document=doc)
                is_authorized = youtube.user_authorized_for_resource(
                    youtube.resources.video.list  # NOT youtube.resources.video.list() AND NOT youtube.resources.videos
                )
        '''
        if user_creds is None:
            user_creds = self.user_creds
        method_scopes = getattr(resource_method, 'scopes', []) 
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

    def __repr__(self):
        return self.title or (self.name + '-' + self.version)

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        try:
            return len(self.resources)
        except AttributeError:
            return 0
