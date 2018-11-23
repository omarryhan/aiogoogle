from pprint import pprint
import json

from .utils import _dict
from .models import Request
from .resource import GoogleAPI
from .auth.managers import Oauth2Manager, ApiKeyManager
from .sessions.aiohttp_session import AiohttpSession


DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'


class Aiogoogle:
    def __init__(self, session_factory=AiohttpSession, api_key=None, user_creds=None, timeout=None):
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

            timeout:
                
                - Timeout for the async context manager
        '''

        self.session_factory = session_factory
        self.timeout = timeout
        self.active_session = None

        # Keys
        self.api_key = api_key
        self.user_creds = user_creds

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
        
        Donwloads and sets a discovery document from: 'https://www.googleapis.com/discovery/v1/apis/{api_name}/{api_version}/rest'
        Makes this a object client to {api_name} + " " + {api_version}
        
        Arguments:

            api_name: API name to discover. e.g.: "youtube"
            
            api_version: API version to discover e.g.: "v3" NOT 3

        '''

        disc_doc_dict = await self._download_discovery_document(api_name, api_version)
        return GoogleAPI(disc_doc_dict, validate)

    #-------- Send Requests ----------#

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
        authorized_requests = [self.api_key_manager.authorize(request, self.api_key) for request in requests]

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

            method (RequestMethod): 
            
                - Method to be checked
                
                e.g.:

                    Correct:
                 
                        youtube = Aiogoogle(discovery_document=ytb_doc)
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


def next_page(token=None, response=None, json_req=False, req_token_name='pageToken', res_token_name='nextPageToken') -> Request:
    '''
    Function given a token **or** a json response returns a request that requests the next resource

    Arguments:

        token (str): one of ('pageToken', 'nextPageToken') that should be found in your response
        
        response (dict): full response not just json

        json_req (dict): Normally, nextPageTokens should be sent in URL query params. If you want it in A json body, set this to True

    Response:

        a request object (Request)
    '''
    res_token = response.json.get(res_token_name, None)
    if not res_token:
        return
    request = Request.from_response(response)
    if json_req:
        request.json[req_token_name] = res_token
    else:
        request._add_query_param(dict(req_token_name=res_token))
    return request