'''

.. note::

    * These are the default auth managers. They won't perform any file io.

    * If you want auth managers with file io capabilities, then you'll have to implement AbstractAuthManager's interface or inherent from this module's classes.
    
    * In most cases you won't need to implement new managers, as by design, credentials are an instance of dict and will only contain json types (str, number, array, ISO8601 datetime, etc) to make it easily serializable.
'''

# To download data in aiogoogle.auth.data.py:
# >>> oauth2_json = requests.get('https://www.googleapis.com/discovery/v1/apis/oauth2/v2/rest').json() 
# >>> google_plus_json = requests.get('https://www.googleapis.com/discovery/v1/apis/plus/v1/rest').json()
# >>> with open('/home/omar/Documents/aiogoogle/aiogoogle/auth/data.py', 'w') as file:
# ...     file.write('OAUTH2_V2_DISCVOCERY_DOC = ' + pprint.pformat(oauth2_json, width=160))
# >>> with open('/home/omar/Documents/aiogoogle/aiogoogle/auth/data.py', 'a') as file:
# ...     file.write('\n\nGOOGLE_PLUS_V1_DISCVOCERY_DOC = ' + pprint.pformat(google_plus_json, width=160))


__all__ = [
    'Oauth2Manager',
    'ApiKeyManager'
]


from urllib import parse
import datetime
try:
    import ujson as json
except:
    import json

from .abc import AbstractOAuth2Manager, AbstractAPIKeyManager
from .creds import UserCreds, ClientCreds
from .data import OAUTH2_V2_DISCVOCERY_DOC, GOOGLE_PLUS_V1_DISCVOCERY_DOC
from ..excs import HTTPError, AuthError
from ..models import Request
from ..resource import GoogleAPI


URLENCODED_CONTENT_TYPE = 'application/x-www-form-urlencoded'
JWT_GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'

REFRESH_GRANT_TYPE = 'refresh_token'
AUTHORIZATION_TYPE = 'code'
GRANT_TYPE = 'authorization_code'

# The URL that provides public certificates for verifying ID tokens issued
# by Google's OAuth 2.0 authorization server.
GOOGLE_OAUTH2_CERTS_URL = 'https://www.googleapis.com/oauth2/v1/certs'

# The URL that provides public certificates for verifying ID tokens issued
# by Firebase and the Google APIs infrastructure
GOOGLE_APIS_CERTS_URL = (
    'https://www.googleapis.com/robot/v1/metadata/x509'
    '/securetoken@system.gserviceaccount.com')

# Used here: https://developers.google.com/identity/protocols/OAuth2WebServer#exchange-authorization-code
AUTH_URI = 'https://accounts.google.com/o/oauth2/v2/auth'
REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'  # Not included in OAuth2 v2 discovery doc
REFRESH_URI = TOKEN_URI
TOKEN_INFO_URI = 'https://www.googleapis.com/oauth2/v4/tokeninfo'

# Used here: https://github.com/googleapis/oauth2client/blob/master/oauth2client/__init__.py  
# Google oauth2client is deprecated in favor of google-oauth-lib & google-auth-library-python
# These aren't used in the code below
GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_DEVICE_URI = 'https://oauth2.googleapis.com/device/code'
GOOGLE_REVOKE_URI = 'https://oauth2.googleapis.com/revoke' 
GOOGLE_TOKEN_URI = 'https://oauth2.googleapis.com/token'
GOOGLE_TOKEN_INFO_URI = 'https://oauth2.googleapis.com/tokeninfo'


class ApiKeyManager(AbstractAPIKeyManager):

    def authorize(self, request, key: str) -> Request:
        # TODO: Do this using urllib or take url fragments into consideration
        if 'key=' in request.url:
            return request
        else:
            url = request.url
            if '?' not in url:
                if url.endswith('/'):
                    url = url[:-1]
                url += '?'
            else:
                url += '&'
            url += f'key={key}'
            request.url = url
            return request

class Oauth2Manager(AbstractOAuth2Manager):
    def __init__(self, session_factory, verify=True):
        self.oauth2_api = GoogleAPI(OAUTH2_V2_DISCVOCERY_DOC, validate=True)
        self.session_factory = session_factory
        self.active_session = None
        self.verify = verify

    async def __aenter__(self):
        self.active_session = await self.session_factory().__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.active_session.__aexit__(*args, **kwargs)
        self.active_session = None

    def authorize(self, request: Request, creds: dict) -> Request:
        if request.headers is None:
            request.headers = {}
        request.headers['Authorization'] = f'Bearer {creds["access_token"]}'
        return request

    def is_ready(self, client_creds):
        '''
        Checks passed ``client_creds`` whether or not the client has enough information to perform OAuth2 Authorization code flow

        Arguments:

            client_creds(aiogoogle.auth.creds.ClientCreds): Client credentials object

        Returns:

            bool: 

        '''
        if client_creds.get('client_id') and \
        client_creds.get('client_secret') and \
        client_creds.get('scopes') and \
        isinstance(client_creds['scopes'], (list, tuple)) and \
        client_creds.get('redirect_uri'):
            return True
        return False

    def build_auth_uri(self, client_creds, state=None, access_type=None, include_granted_scopes=None, login_hint=None, prompt=None) -> (str, dict):
        scopes = ' '.join(client_creds['scopes'])
        uri = AUTH_URI + f'?redirect_uri={client_creds["redirect_uri"]}&scope={scopes}&'
        for param_name, param in {
            'client_id': client_creds['client_id'],
            'response_type': AUTHORIZATION_TYPE,
            'state': state,
            'access_type': access_type,
            'include_granted_scopes': json.dumps(include_granted_scopes),
            'login_hint': login_hint,
            'prompt': prompt
        }.items():
            if param is not None:
                uri += '&' 
                uri += parse.urlencode({param_name: param})
        return uri

    async def build_user_creds(self, grant, client_creds) -> dict:
        request = self._build_user_creds_req(grant, client_creds)
        if self.active_session is None:
            async with self.session_factory() as sess:
                json_res = await sess.send(request)
        else:
            json_res = await self.active_session.send(request)
        return self._build_user_creds_from_res(json_res)

    def _build_user_creds_req(self, grant, client_creds) -> Request:
        data = dict(
                code=grant,
                client_id=client_creds['client_id'],
                client_secret=client_creds['client_secret'],
                redirect_uri=client_creds['redirect_uri'],
                grant_type=GRANT_TYPE
            )
        headers = {'content-type': URLENCODED_CONTENT_TYPE}
        method = 'POST'
        url = TOKEN_URI
        data = data
        return Request(method, url, headers, data=data)

    def _build_user_creds_from_res(self, json_res):
        scopes = json_res.pop('scope').split(' ')
        user_creds = UserCreds(**json_res, scopes=scopes)
        # Idk why, but sometimes google returns these json params empty
        user_creds['token_uri'] = TOKEN_URI if user_creds.get('token_uri') is None else None
        user_creds['token_info_uri'] = TOKEN_INFO_URI if not user_creds.get('token_info_uri') else None
        user_creds['revoke_uri'] = REVOKE_URI if not user_creds.get('revoke_uri') else None
        user_creds['expires_at'] = self._get_expires_at(user_creds['expires_in'])
        return user_creds
    
    def _get_expires_at(self, expires_in):
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        # substract 2 mins to account for network latency and thus avoiding 401 responses
        expires_at -= datetime.timedelta(seconds=120)
        return expires_at.isoformat()

    def authorized_for_method(self, method, user_creds) -> bool:
        '''
        Checks if oauth2 user_creds object has sufficient scopes for a method call.
        
        .. note:: 
        
            This method doesn't check whether creds are refreshed or valid. As this is done automatically before each request.

        e.g.

            **Correct:**

            .. code-block:: python3
        
                is_authorized = authorized_for_method(youtube.resources.video.list)
            
            **NOT correct:**

            .. code-block:: python3

                is_authorized = authorized_for_method(youtube.resources.video.list())

            **AND NOT correct:**

            .. code-block:: python3

                is_authorized = authorized_for_method(youtube.resources.videos)


        Arguments:

            method (aiogoogle.resource.Method): Method to be checked

            user_credentials (aiogoogle.auth.creds.UserCreds): User Credentials with scopes item

        Returns:

            bool:

        '''
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

    def is_expired(self, creds) -> bool:
        expires_at = datetime.datetime.fromisoformat(creds['expires_at'])
        if datetime.datetime.utcnow() >= expires_at:
            return True
        else:
            return False

    async def refresh(self, user_creds, client_creds):
        request = self._build_refresh_request(user_creds, client_creds)
        if self.active_session is None:
            async with self.session_factory() as sess:
                json_res = await sess.send(request)
        else:
            json_res = await self.active_session.send(request)
        return self._build_user_creds_from_res(json_res)

    def _build_refresh_request(self, user_creds, client_creds):
        data = dict(
            grant_type=REFRESH_GRANT_TYPE,
            client_id=client_creds["client_id"],
            client_secret=(client_creds["client_secret"]),
            refresh_token=(user_creds["refresh_token"])
        )
        method = 'POST'
        headers = {'content-type': URLENCODED_CONTENT_TYPE}
        return Request(method, REFRESH_URI, headers, data=data)

    def _build_revoke_request(self, user_creds):
        return Request(
            method='POST',
            headers={'content-type': URLENCODED_CONTENT_TYPE},
            url=REVOKE_URI,
            data=dict(token=user_creds['access_token'])
        )

    async def revoke(self, user_creds):
        request = self._build_revoke_request(user_creds)
        if self.active_session is None:
            async with self.session_factory() as sess:
                json_res = await sess.send(request)
        else:
            json_res = await self.active_session.send(request)
        return json_res

    #---- Only 4 methods OAuth2 V2 -------------------------------------------
    # First 2 methods shouldn't belong here 

    async def get_open_id_certs(self):
        if self.active_session is None:
            async with self.session_factory() as sess:
                certs = await sess.send(self.oauth2_api.getCertForOpenIdConnect())
        else:
            certs = await self.active_session.send(self.oauth2_api.getCertForOpenIdConnect())
        return certs

    async def get_token_info(self, user_creds):
        req = self.oauth2_api.tokenInfo(
            access_token=user_creds.get('access_token'),
            id_token=user_creds.get('id_token'),
            token_handle=user_creds.get('token_handle')
        )
        if self.active_session is None:
            async with self.session_factory() as sess:
                token_info = await sess.send(req)
        else:
            token_info = await self.active_session.send(req)
        return token_info

    async def get_user_info(self, user_creds):
        req = self.oauth2_api.userinfo.get()
        authorized_req = self.authorize(req, user_creds)
        if self.active_session is None:
            async with self.session_factory() as sess:
                user_info = await sess.send(authorized_req)
        else:
            user_info = await self.active_session.send(authorized_req)
        return user_info

    async def get_me_info(self, user_creds):
        req = self.oauth2_api.userinfo.v2.me.get()
        authorized_req = self.authorize(req, user_creds)
        if self.active_session is None:
            async with self.session_factory() as sess:
                me_info = await sess.send(authorized_req)
        else:
            me_info = await self.active_session.send(authorized_req)
        return me_info

    #---- /Only 4 methods OAuth2 V2 -------------------------------------------

class OpenIDManager(Oauth2Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.google_plus = GoogleAPI(GOOGLE_PLUS_V1_DISCVOCERY_DOC)

    def jwt_grant(request, token_uri, assertion):
        """Implements the JWT Profile for OAuth 2.0 Authorization Grants.

        For more details, see `rfc7523 section 4`_.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            token_uri (str): The OAuth 2.0 authorizations server's token endpoint
                URI.
            assertion (str): The OAuth 2.0 assertion.

        Returns:
            Tuple[str, Optional[datetime], Mapping[str, str]]: The access token,
                expiration, and additional data returned by the token endpoint.

        Raises:
            google.auth.exceptions.RefreshError: If the token endpoint returned
                an error.

        .. _rfc7523 section 4: https://tools.ietf.org/html/rfc7523#section-4
        """
        body = {
            'assertion': assertion,
            'grant_type': JWT_GRANT_TYPE,
        }

        response_data = _token_endpoint_request(request, token_uri, body)

        try:
            access_token = response_data['access_token']
        except KeyError as caught_exc:
            new_exc = exceptions.RefreshError(
                'No access token in response.', response_data)
            six.raise_from(new_exc, caught_exc)

        expiry = _parse_expiry(response_data)

        return access_token, expiry, response_data

    def id_token_jwt_grant(self, request, token_uri, assertion):
        """Implements the JWT Profile for OAuth 2.0 Authorization Grants, but
        requests an OpenID Connect ID Token instead of an access token.

        This is a variant on the standard JWT Profile that is currently unique
        to Google. This was added for the benefit of authenticating to services
        that require ID Tokens instead of access tokens or JWT bearer tokens.

        Args:
            request (google.auth.transport.Request): A callable used to make
                HTTP requests.
            token_uri (str): The OAuth 2.0 authorization server's token endpoint
                URI.
            assertion (str): JWT token signed by a service account. The token's
                payload must include a ``target_audience`` claim.

        Returns:
            Tuple[str, Optional[datetime], Mapping[str, str]]:
                The (encoded) Open ID Connect ID Token, expiration, and additional
                data returned by the endpoint.

        Raises:
            google.auth.exceptions.RefreshError: If the token endpoint returned
                an error.
        """
        body = {
            'assertion': assertion,
            'grant_type': JWT_GRANT_TYPE,
        }

        response_data = _token_endpoint_request(request, token_uri, body)

        try:
            id_token = response_data['id_token']
        except KeyError as caught_exc:
            new_exc = exceptions.RefreshError(
                'No ID token in response.', response_data)
            six.raise_from(new_exc, caught_exc)

        payload = jwt.decode(id_token, verify=False)
        expiry = datetime.datetime.utcfromtimestamp(payload['exp'])

        return id_token, expiry, response_data


    """Google ID Token helpers.

    Provides support for verifying `OpenID Connect ID Tokens`_, especially ones
    generated by Google infrastructure.

    To parse and verify an ID Token issued by Google's OAuth 2.0 authorization
    server use :func:`verify_oauth2_token`. To verify an ID Token issued by
    Firebase, use :func:`verify_firebase_token`.

    A general purpose ID Token verifier is available as :func:`verify_token`.

    Example::

        from google.oauth2 import id_token
        from google.auth.transport import requests

        request = requests.Request()

        id_info = id_token.verify_oauth2_token(
            token, request, 'my-client-id.example.com')

        if id_info['iss'] != 'https://accounts.google.com':
            raise ValueError('Wrong issuer.')

        userid = id_info['sub']

    By default, this will re-fetch certificates for each verification. Because
    Google's public keys are only changed infrequently (on the order of once per
    day), you may wish to take advantage of caching to reduce latency and the
    potential for network errors. This can be accomplished using an external
    library like `CacheControl`_ to create a cache-aware
    :class:`google.auth.transport.Request`::

        import cachecontrol
        import google.auth.transport.requests
        import requests

        session = requests.session()
        cached_session = cachecontrol.CacheControl(session)
        request = google.auth.transport.requests.Request(session=cached_session)

    .. _OpenID Connect ID Token:
        http://openid.net/specs/openid-connect-core-1_0.html#IDToken
    .. _CacheControl: https://cachecontrol.readthedocs.io
    """

    def verify_token(id_token, request, audience=None,
                    certs_url=GOOGLE_OAUTH2_CERTS_URL):
        """Verifies an ID token and returns the decoded token.

        Args:
            id_token (Union[str, bytes]): The encoded token.
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
            audience (str): The audience that this token is intended for. If None
                then the audience is not verified.
            certs_url (str): The URL that specifies the certificates to use to
                verify the token. This URL should return JSON in the format of
                ``{'key id': 'x509 certificate'}``.

        Returns:
            Mapping[str, Any]: The decoded token.
        """
        certs = _fetch_certs(request, certs_url)

        return jwt.decode(id_token, certs=certs, audience=audience)


    def verify_oauth2_token(id_token, request, audience=None):
        """Verifies an ID Token issued by Google's OAuth 2.0 authorization server.

        Args:
            id_token (Union[str, bytes]): The encoded token.
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
            audience (str): The audience that this token is intended for. This is
                typically your application's OAuth 2.0 client ID. If None then the
                audience is not verified.

        Returns:
            Mapping[str, Any]: The decoded token.
        """
        return verify_token(
            id_token, request, audience=audience,
            certs_url=GOOGLE_OAUTH2_CERTS_URL)


    def verify_firebase_token(id_token, request, audience=None):
        """Verifies an ID Token issued by Firebase Authentication.

        Args:
            id_token (Union[str, bytes]): The encoded token.
            request (google.auth.transport.Request): The object used to make
                HTTP requests.
            audience (str): The audience that this token is intended for. This is
                typically your Firebase application ID. If None then the audience
                is not verified.

        Returns:
            Mapping[str, Any]: The decoded token.
        """
        return verify_token(
            id_token, request, audience=audience, certs_url=GOOGLE_APIS_CERTS_URL)
