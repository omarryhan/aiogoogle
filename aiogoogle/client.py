__all__ = ["Aiogoogle"]


from .resource import GoogleAPI
from .auth.managers import Oauth2Manager, ApiKeyManager, OpenIdConnectManager, ServiceAccountManager
from .sessions.aiohttp_session import AiohttpSession
from .data import DISCOVERY_SERVICE_V1_DISCOVERY_DOC


# Discovery doc reference https://developers.google.com/discovery/v1/reference/apis


class Aiogoogle:
    """
    Main entry point for Aiogoogle.

    This class acts as tiny wrapper around:

        1. Discovery Service v1 API
        2. Aiogoogle's OAuth2 manager
        3. Aiogoogle's API key manager
        4. Aiogoogle's OpenID Connect manager
        5. Aiogoogle's service account manager 
        6. One of Aiogoogle's implementations of a session object

    Arguments:

        session_factory (aiogoogle.sessions.abc.AbstractSession): AbstractSession Implementation. Defaults to ``aiogoogle.sessions.aiohttp_session.AiohttpSession``

        api_key (aiogoogle.auth.creds.ApiKey): Google API key
        
        user_creds (aiogoogle.auth.creds.UserCreds): OAuth2 cser credentials 

        client_creds (aiogoogle.auth.creds.ClientCreds): OAuth2 client credentials

        service_account_creds (aiogoogle.auth.creds.ServiceAccountCreds): Service account credentials
        
    Note: 
    
        In case you want to instantiate a custom session with initial parameters, you can pass an anonymous factory. e.g. ::
        
            >>> sess = lambda: Session(your_custome_arg, your_custom_kwarg=True)
            >>> aiogoogle = Aiogoogle(session_factory=sess)
    """

    def __init__(
        self,
        session_factory=AiohttpSession,
        api_key=None,
        user_creds=None,
        client_creds=None,
        service_account_creds=None,
    ):

        self.session_factory = session_factory
        self.active_session = None

        # Keys
        self.api_key = api_key
        self.user_creds = user_creds
        self.client_creds = client_creds
        self.service_account_creds = service_account_creds

        # Auth managers
        self.api_key_manager = ApiKeyManager(api_key=self.api_key)
        self.oauth2 = Oauth2Manager(
            self.session_factory, client_creds=self.client_creds
        )
        self.openid_connect = OpenIdConnectManager(
            self.session_factory, client_creds=self.client_creds
        )
        self.service_account_manager = ServiceAccountManager(
            self.session_factory, creds=self.service_account_creds
        )

        # Discovery service
        self.discovery_service = GoogleAPI(DISCOVERY_SERVICE_V1_DISCOVERY_DOC)

    # -------- Only 2 methods of Discover Service V1 ---------#

    async def list_api(self, name, preferred=None, fields=None):
        """
        https://developers.google.com/discovery/v1/reference/apis/list

        The discovery.apis.list method returns the list all APIs supported by the Google APIs Discovery Service.
        
        The data for each entry is a subset of the Discovery Document for that API, and the list provides a directory of supported APIs.
        
        If a specific API has multiple versions, each of the versions has its own entry in the list.

        Example:

            ::

                >>> await aiogoogle.list_api('youtube')

                {
                    "kind": "discovery#directoryList",
                    "discoveryVersion": "v1",
                    "items": [
                        {
                            "kind": "discovery#directoryItem",
                            "id": "youtube:v3",
                            "name": "youtube",
                            "version": "v3",
                            "title": "YouTube Data API",
                            "description": "Supports core YouTube features, such as uploading videos, creating and managing playlists, searching for content, and much more.",
                            "discoveryRestUrl": "https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest",
                            "discoveryLink": "./apis/youtube/v3/rest",
                            "icons": {
                                "x16": "https://www.google.com/images/icons/product/youtube-16.png",
                                "x32": "https://www.google.com/images/icons/product/youtube-32.png"
                            },
                            "documentationLink": "https://developers.google.com/youtube/v3",
                            "preferred": true
                        }
                    ]
                }

        Arguments:

            name (str): Only include APIs with the given name.

            preferred (bool): Return only the preferred version of an API.  "false" by default.

            fields (str): Selector specifying which fields to include in a partial response.

        Returns:

            dict:

        Raises:

            aiogoogle.excs.HTTPError
        """

        request = self.discovery_service.apis.list(
            name=name, preferred=preferred, fields=fields
        )
        return await self.as_anon(request)

    async def discover(self, api_name, api_version=None, validate=False):
        """ 
        Donwloads a discovery document from Google's Discovery Service V1 and sets it a ``aiogoogle.resource.GoogleAPI``

        Note:

            It is recommended that you explicitly specify an API version.
            
            When you leave the API version as None, Aiogoogle uses the ``list_api`` method to search for the best fit version of the given API name.
            
            This will result in sending two http requests instead of just one.
        
        Arguments:

            api_name (str): API name to discover. *e.g.: "youtube"*
            
            api_version (str): API version to discover *e.g.: "v3" not "3" and not 3*

            validate (bool): Set this to True to use this lib's built in parameter validation logic. Note that you shouldn't rely on this for critical user input validation.
            
        Returns:

            aiogoogle.resource.GoogleAPI: An object that will then be used to create API requests

        Raises:

            aiogoogle.excs.HTTPError

        """

        if api_version is None:
            # Search for name in self.list_api and return best match
            discovery_list = await self.list_api(api_name, preferred=True)

            if discovery_list["items"]:
                api_name = discovery_list["items"][0]["name"]
                api_version = discovery_list["items"][0]["version"]
            else:
                raise ValueError("Invalid API name")

        request = self.discovery_service.apis.getRest(
            api=api_name, version=api_version, validate=False
        )

        discovery_docuemnt = await self.as_anon(request)

        return GoogleAPI(discovery_docuemnt, validate)

    # -------- Send Requests ----------#

    async def as_user(self, *requests, timeout=None, full_res=False, raise_for_status=True, user_creds=None):
        """ 
        Sends requests on behalf of ``self.user_creds`` (OAuth2)
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_res (bool):

                If True, returns full HTTP response object instead of returning it's content

            raise_for_status (bool):

                If True, raises an HTTP error on HTTP status codes >= 400

            user_creds (aiogoogle.auth.creds.UserCreds):

                If you pass user_creds here, they will only be used for this one request.

        Returns:

            aiogoogle.models.Response:
        """
        user_creds = user_creds or self.user_creds
        if user_creds is None:
            raise TypeError("No user credentials were found")

        # Refresh credentials
        if (
            user_creds.get("expires_at") is None
            or (user_creds.get("expires_at") and self.oauth2.is_expired(user_creds) is True)
        ):
            user_creds = await self.oauth2.refresh(
                user_creds, client_creds=self.client_creds
            )

            # Set refreshed user_creds if ones were already existing
            if self.user_creds is not None:
                self.user_creds = user_creds

        authorized_requests = [
            self.oauth2.authorize(request, user_creds) for request in requests
        ]

        return await self.send(
            *authorized_requests,
            timeout=timeout,
            full_res=full_res,
            raise_for_status=raise_for_status,
            session_factory=self.session_factory
        )

    async def as_service_account(
            self, *requests, timeout=None, full_res=False, raise_for_status=True, service_account_creds=None):
        """ 
        Sends requests on behalf of ``self.user_creds`` (OAuth2)
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_res (bool):

                If True, returns full HTTP response object instead of returning it's content

            raise_for_status (bool):

                If True, raises an HTTP error on HTTP status codes >= 400

            service_account_creds (aiogoogle.auth.creds.ServiceAccountCreds):

                You only have to pass ``service_account_creds`` once, either here or when instantiating an instance of Aiogoogle.

        Returns:

            aiogoogle.models.Response:
        """
        service_account_creds = service_account_creds or self.service_account_creds
        if service_account_creds is None:
            raise TypeError("Please pass service account creds")

        await self.service_account_manager.refresh()

        authorized_requests = [
            self.service_account_manager.authorize(request) for request in requests
        ]

        return await self.send(
            *authorized_requests,
            timeout=timeout,
            full_res=full_res,
            raise_for_status=raise_for_status,
            session_factory=self.session_factory
        )

    async def as_api_key(self, *requests, timeout=None, full_res=False, raise_for_status=True, api_key=None):
        """ 
        Sends requests on behalf of ``self.api_key`` (OAuth2)
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_res (bool):

                If True, returns full HTTP response object instead of returning it's content

            raise_for_status (bool):

                If True, raises an HTTP error on HTTP status codes >= 400

            api_key (string):

                If you pass an API key here, it will only be used for this one request.

        Returns:

            aiogoogle.models.Response:
        """
        api_key = api_key or self.api_key
        if api_key is None:
            raise TypeError("Please pass an API key")

        authorized_requests = [
            self.api_key_manager.authorize(request, api_key)
            for request in requests
        ]

        return await self.send(
            *authorized_requests,
            timeout=timeout,
            full_res=full_res,
            raise_for_status=raise_for_status,
            session_factory=self.session_factory
        )

    async def as_anon(self, *requests, timeout=None, full_res=False, raise_for_status=True):
        """ 
        Sends unauthorized requests
        
        Arguments:

            *requests (aiogoogle.models.Request):

                Requests objects typically created by ``aiogoogle.resource.Method.__call__``

            timeout (int):

                Total timeout for all the requests being sent

            full_res (bool):

                If True, returns full HTTP response object instead of returning it's content

            raise_for_status (bool):

                If True, raises an HTTP error on HTTP status codes >= 400

        Returns:

            aiogoogle.models.Response:
        """
        return await self.send(
            *requests,
            timeout=timeout,
            full_res=full_res,
            raise_for_status=raise_for_status,
            session_factory=self.session_factory
        )

    async def _ensure_session_set(self):
        if self.active_session is None:
            self.active_session = self.session_factory()

    async def send(self, *args, **kwargs):
        await self._ensure_session_set()
        return await self.active_session.send(*args, **kwargs)

    async def __aenter__(self):
        await self._ensure_session_set()
        await self.active_session.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.active_session.__aexit__(*args)
        # Had to add this because there's no use of keeping a closed session
        # Closed sessions cannot be reopened, so it's better to just get rid of the object
        self.active_session = None
