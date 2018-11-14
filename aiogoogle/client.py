from pprint import pprint
import json

from .utils import _dict
from .models import Request, Resources
from .auth.managers import Oauth2Manager, ServiceAccountManager, ApiKeyManager
from .sessions.aiohttp_session import AiohttpSession


DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'


class DiscoveryClient:
    def __init__(self, session_factory=AiohttpSession, api_key=None, user_creds=None, client_creds=None, service_account_creds=None, discovery_document={}):
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
        '''

        self.discovery_document = discovery_document
        self.session_factory = session_factory

        # Auth managers
        self.api_key_manager = ApiKeyManager(self.session_factory)
        self.service_account_manager = ServiceAccountManager(self.session_factory)
        self.oauth2_manager = Oauth2Manager(self.session_factory)

        # Keys
        self.api_key = api_key
        self.user_creds = user_creds
        self.client_creds = client_creds
        self.servivde_account_creds = service_account_creds

    #-------- Discovery Document ---------#

    @property
    def discovery_document(self):
        return self._discovery_document

    @discovery_document.setter
    def discovery_document(self, discovery_document):
        self._discovery_document = discovery_document

        # save some data from the discovery document to main client to minimize memory consumption when many resources and resource.methods are instantiated
        self._schema = self._discovery_document.get('schema')
        self._auth = self._discovery_document.get('auth')
        self._global_parameters = self._discovery_document.get('parameters')

        # Make a gateway object that will be responsible for creating requests that access resources from google's apis.
        self.resources = Resources(self._discovery_document, self._schema, self._auth, self._global_parameters)

    async def _download_discovery_document(self, api_name, api_version):
        url = DISCOVERY_URL.format(api_name=api_name, api_version=api_version)
        request = Request(method='GET', url=url)
        return await self.send_unauthorized(request)

    async def discover(self, api_name, api_version):
        ''' Downloads discovery document and sets it to self '''
        self.discovery_document = await self._download_discovery_document(api_name, api_version)

    #-------- Send Requests ----------#

    async def send_as_client(self, *requests, return_full_response=False, return_tasks=False):
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
            responses = await session.send(*authorized_requests, return_full_response=return_full_response, return_tasks=return_tasks)
        return responses


    async def send_as_user(self, *requests, return_full_response=False, return_tasks=False):
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
            responses = await session.send(*authorized_requests, return_full_response=return_full_response, return_tasks=return_tasks)
        return responses

    async def send_as_service_account(self, *requests, return_full_response=False, return_tasks=False):
        '''
        Sends requests on behalf og self.service_account_creds
        '''
        raise NotImplementedError

    async def send_as_api(self, *requests, return_full_response=False, return_tasks=False):
        '''
        Sends requests on behalf of the owner of self.api_key
        '''

        # Authorize requests
        authorized_requests = [self.api_key_manager.authorize_request(request, self.api_key) for request in requests]

        # Send authorized requests
        async with self.session_factory() as session:
            responses = await session.send(*authorized_requests, return_full_response=return_full_response, return_tasks=return_tasks)
        return responses

    async def send_unauthorized(self, *requests, return_full_response=False, return_tasks=False):
        '''
        Sends unauthorized requests
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_full_response=return_full_response, return_tasks=return_tasks)
        return responses

    #------------------- Some Properties -------------------#

    @property
    def name(self) -> str:
        return self.discovery_document.get('name')
    
    @property
    def version(self) -> str:
        return self.discovery_document.get('version')

    #-------------- Helper methods ------------------#

    def is_authorized_for_resource(self, resource_object, creds_name: str) -> bool:
        '''
        checks with appropriate oauth manager if user will be authorized with the currently available creds
            - Checks whether appropriate creds exist
            - Checks if relevant creds object has sufficient scope
        However:
            - Doesn't check whether creds are refreshed

        e.g. input:
            
                youtube = DiscoveryClient(discovery_document=youtube_disc_doc)
                result = youtube.is_authorized_for_resource(
                    youtube.resources.video  # NOT youtube.resources.video.list()
                )
        '''
        pass