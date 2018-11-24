__all__ = [
    'Aiogoogle'
]


from pprint import pprint
import json

from .utils import _dict
from .models import Request
from .resource import GoogleAPI
from .auth.managers import Oauth2Manager, ApiKeyManager
from .sessions.aiohttp_session import AiohttpSession



DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'


class Aiogoogle:
    '''
    Arguments:

        session_factory (aiogoogle.sessions.abc.AbstractSession): AbstractSession Implementation. Defaults to ``aiogoogle.sessions.aiohttp_session.AiohttpSession``

        api_key (aiogoogle.auth.creds.ApiKey): Google API key
        
        user_creds (aiogoogle.auth.creds.UserCreds): OAuth2 User Credentials 

        client_creds (aiogoogle.auth.creds.ClientCreds): OAuth2 Client Credentials
        
        timeout (int): Timeout for this class's async context manager
            
    Hint: 
    
        In case you want to instantiate a custom session with initial parameters, you can:

            - Pass an anonymous factory. e.g.: ``lambda: Session(your_custome_arg, your_custom_kwarg=True)``
    '''

    def __init__(self, session_factory=AiohttpSession, api_key=None, user_creds=None, client_creds=None, timeout=None):

        self.session_factory = session_factory
        self.timeout = timeout
        self.active_session = None

        # Keys
        self.api_key = api_key
        self.user_creds = user_creds
        self.client_creds = client_creds

        # Auth managers
        self.api_key_manager = ApiKeyManager()
        self.oauth2 = Oauth2Manager(self.session_factory)

    #-------- Discovery Document ---------#

    async def _download_discovery_document(self, api_name, api_version):
        url = DISCOVERY_URL.format(api_name=api_name, api_version=api_version)
        request = Request(method='GET', url=url)
        
        if self.active_session is None:
            async with self:
                discovery_docuemnt = await self.as_anon(request)
        else:
            discovery_docuemnt = await self.as_anon(request)
        return discovery_docuemnt

    async def discover(self, api_name, api_version, validate=True):
        ''' 
        
        Donwloads a discovery document from Google's Discovery Service V1 and sets it a ``aiogoogle.resource.GoogleAPI``
        
        Arguments:

            api_name (str): API name to discover. *e.g.: "youtube"*
            
            api_version (str): API version to discover *e.g.: "v3" not "3" and not 3*
            
        Returns:

            aiogoogle.resource.GoogleAPI: An object that will then be used to create ``<api_name><api_version>`` requests

        '''

        disc_doc_dict = await self._download_discovery_document(api_name, api_version)
        return GoogleAPI(disc_doc_dict, validate)

    #-------- Send Requests ----------#

    async def as_user(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends requests on behalf of ``self.user_creds`` (OAuth2)
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_resp (bool):

                If True, returns full HTTP response object instead of returning it's content

        Returns:

            aiogoogle.models.Response:
        '''
        # Refresh credentials
        self.user_creds = self.oauth2.refresh(
            self.user_creds,
            client_creds=self.client_creds
        )

        # Authroize requests
        authorized_requests = [self.oauth2.authorize(request, self.user_creds) for request in requests]

        # Send authorized requests
        return await self.active_session.send(*authorized_requests, timeout=timeout, return_full_http_response=full_resp)

    async def as_api_key(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends requests on behalf of ``self.api_key`` (OAuth2)
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_resp (bool):

                If True, returns full HTTP response object instead of returning it's content

        Returns:

            aiogoogle.models.Response:
        '''

        # Authorize requests
        authorized_requests = [self.api_key_manager.authorize(request, self.api_key) for request in requests]

        # Send authorized requests
        return await self.active_session.send(*authorized_requests, timeout=timeout, return_full_http_response=full_resp)

    async def as_anon(self, *requests, timeout=None, full_resp=False):
        ''' 
        Sends an unauthorized request
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_resp (bool):

                If True, returns full HTTP response object instead of returning it's content

        Returns:

            aiogoogle.models.Response:
        '''
        return await self.active_session.send(*requests, timeout=timeout, return_full_http_response=full_resp)

    def user_authorized_for_method(self, method, user_creds=None) -> bool:
        '''
        Checks if oauth2 user_creds object has sufficient scopes for a method call.
        
        .. note:: 
        
            This method doesn't check whether creds are refreshed or valid. As this is done automatically before each request.

        e.g.

            **Correct:**

            .. code-block:: python3
        
                is_authorized = youtube.user_authorized_for_resource(
                    youtube.resources.video.list
                )
            
            **NOT correct:**

            .. code-block:: python3

                is_authorized = youtube.user_authorized_for_resource(
                    youtube.resources.video.list()
                )

            **AND NOT correct:**

            .. code-block:: python3

                is_authorized = youtube.user_authorized_for_resource(
                    youtube.resources.videos
                )


        Arguments:

            method (aiogoogle.resource.Method): Method to be checked

            user_credentials (aiogoogle.auth.creds.UserCreds, dict): User Credentials

        Returns:

            bool:

        '''
        if user_creds is None:
            user_creds = self.user_creds
        method_scopes = method['scopes'] or []
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

    async def __aenter__(self):
        self.active_session = await self.session_factory(timeout=self.timeout).__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.active_session.__aexit__(*args, **kwargs)
        self.active_session = None
