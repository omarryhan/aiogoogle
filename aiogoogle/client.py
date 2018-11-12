from .utils import _dict
from .models import Request, Resources
from .auth.managers import Oauth2Manager, ServiceAccountManager, ApiKeyManager
from .auth.utils import refresh_creds, authorize_requests
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
        self.api_key_manager = ApiKeyManager()
        self.service_account_manager = ServiceAccountManager()
        self.oauth2_manager = Oauth2Manager()

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
        self._schema = discovery_document.get('schema')
        self._auth = discovery_document.get('auth')
        self._global_parameters = discovery_document.get('parameters')

        # Make a gateway object that will be responsible for creating requests that access resources from google's apis.
        self.resources = Resources(self._discovery_document, self._schema, self._auth, self._global_parameters)

    async def _download_discovery_document(self, api_name, api_version):
        url = DISCOVERY_URL.format(api_name, api_version)
        request = Request(method='GET', url=url)
        return await self.send_unauthorized(request)

    async def discover(self, api_name, api_version):
        ''' Downloads discovery document and sets it to self '''
        self.discovery_document = await self._download_discovery_document(api_name, api_version)

    #-------- Send Requests ----------#

    @authorize_requests(creds_name='client_creds', manager_name='oauth2_manager')
    @refresh_creds(creds_name='client_creds', manager_name='oauth2_manager')
    async def send_as_client(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        ''' 
        Sends requests on behalf of self.client_creds
        Uses OAuth2
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_json_only=return_json_only, raise_for_status=raise_for_status, return_tasks=return_tasks)
        return responses


    @authorize_requests(creds_name='user_creds', manager_name='oauth2_manager')
    @refresh_creds(creds_name='user_creds', manager_name='oauth2_manager')
    async def send_as_user(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        '''
        Sends requests on behalf of self.user_creds
        Uses OAuth2
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_json_only=return_json_only, raise_for_status=raise_for_status, return_tasks=return_tasks)
        return responses

    @authorize_requests(creds_name='service_account_creds', manager_name='service_account_manager')
    @refresh_creds(creds_name='service_account_creds', manager_name='service_account_manager')
    async def send_as_service_account(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        '''
        Sends requests on behalf og self.service_account_creds
        '''
        raise NotImplementedError

    @authorize_requests(creds_name='api_key', manager_name='api_key_manager')
    async def send_as_api(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        '''
        Sends requests on behalf of the owner of self.api_key
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_json_only=return_json_only, raise_for_status=raise_for_status, return_tasks=return_tasks)

    async def send_unauthorized(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        '''
        Sends unauthorized requests
        '''
        async with self.session_factory() as session:
            responses = await session.send(*requests, return_json_only=return_json_only, raise_for_status=raise_for_status, return_tasks=return_tasks)
