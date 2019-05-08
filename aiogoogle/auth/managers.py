"""
.. note::

    * These are the default auth managers. They won't perform any file io.

    * If you want auth managers with file io capabilities, then you'll have to implement AbstractAuthManager's interface or inherent from any of this module's managers.
    
    * In most cases you won't need to implement new managers for file io, as by design, credentials are an instance of dict and will only contain json types (str, number, array, JSONSCHEMA datetime and ISO8601 datetime, etc) to make it easily serializable.
"""

__all__ = ["ApiKeyManager", "Oauth2Manager", "OpenIdConnectManager"]

from urllib import parse
import datetime

try:
    import ujson as json
except:
    import json
from google.auth import jwt

from .abc import (
    AbstractOAuth2Manager,
    AbstractAPIKeyManager,
    AbstractOpenIdConnectManager,
)
from .creds import UserCreds, ClientCreds
from .data import OAUTH2_V2_DISCVOCERY_DOC, WELLKNOWN_OPENID_CONFIGS
from ..excs import HTTPError, AuthError
from ..models import Request
from ..resource import GoogleAPI
from ..sessions.aiohttp_session import AiohttpSession


# ID token contents: https://openid.net/specs/openid-connect-core-1_0.html#IDToken
# JWK reference: https://tools.ietf.org/html/rfc7517
# Google OpenID discovery doc reference: https://developers.google.com/identity/protocols/OpenIDConnect#discovery

# discovery docs
OPENID_CONFIGS_DISCOVERY_DOC_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
OAUTH2_DISCOVERY_DOCUMENT_URL = (
    "https://www.googleapis.com/discovery/v1/apis/oauth2/v2/rest"
)

# Response types
AUTH_CODE_RESPONSE_TYPE = "code"  # token for implicit flow and and openid for OpenID
HYBRID_RESPONSE_TYPE = "code id_token"

# Grant types
AUTH_CODE_GRANT_TYPE = "authorization_code"
REFRESH_GRANT_TYPE = "refresh_token"
JWT_GRANT_TYPE = (
    "urn:ietf:params:oauth:grant-type:jwt-bearer"
)  # https://tools.ietf.org/html/rfc7523#section-4  OAuth JWT Assertion Profiles

# Other types
URLENCODED_CONTENT_TYPE = "application/x-www-form-urlencoded"
# _Installed Application Authorization Flow:
#  https://developers.google.com/api-client-library/python/auth/installed-app
OOB_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

DEFAULT_ISS = "https://accounts.google.com"

## The URL that provides public certificates for verifying ID tokens issued
## by Google's OAuth 2.0 authorization server.
GOOGLE_OAUTH2_CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"
# GOOGLE_OAUTH2_CERTS_URL_V3 = 'https://www.googleapis.com/oauth2/v3/certs'

# Used here: https://developers.google.com/identity/protocols/OAuth2WebServer#exchange-authorization-code
# AUTH_URI = 'https://accounts.google.com/o/oauth2/v2/auth'
# REVOKE_URI = 'https://accounts.google.com/o/oauth2/revoke'
# TOKEN_URI = REFRESH_URI = 'https://www.googleapis.com/oauth2/v4/token'  # Not included in OAuth2 v2 discovery doc
TOKEN_INFO_URI = "https://www.googleapis.com/oauth2/v4/tokeninfo"

## Used here: https://github.com/googleapis/oauth2client/blob/master/oauth2client/__init__.py
## Google oauth2client is deprecated in favor of google-oauth-lib & google-auth-library-python
## These aren't used in the code below in favor of the urls above
# GOOGLE_AUTH_URI = 'https://accounts.google.com/o/oauth2/v2/auth'
# GOOGLE_DEVICE_URI = 'https://oauth2.googleapis.com/device/code'
# GOOGLE_REVOKE_URI = 'https://oauth2.googleapis.com/revoke'
# GOOGLE_TOKEN_URI = 'https://oauth2.googleapis.com/token'
# GOOGLE_TOKEN_INFO_URI = 'https://oauth2.googleapis.com/tokeninfo'


class ApiKeyManager(AbstractAPIKeyManager):
    def __init__(self, api_key=None):
        self.key = api_key

    @staticmethod
    def authorize(request, key=None) -> Request:
        key = key or self.key
        if "key=" in request.url:
            return request
        else:
            url = request.url
            if "?" not in url:
                if url.endswith("/"):
                    url = url[:-1]
                url += "?"
            else:
                url += "&"
            url += f"key={key}"
            request.url = url
            return request


class Oauth2Manager(AbstractOAuth2Manager):
    def __init__(self, session_factory=AiohttpSession, verify=True, client_creds=None):
        self.oauth2_api = GoogleAPI(OAUTH2_V2_DISCVOCERY_DOC)
        self.openid_configs = WELLKNOWN_OPENID_CONFIGS
        self.session_factory = session_factory
        self.active_session = None
        self.verify = verify
        self.client_creds = client_creds

    def __getitem__(self, key):
        """
        Gets Google's openID configs

        Example:

            * response_types_supported
            
            * scopes_supported
            
            * claims_supported
        """
        try:
            return self.openid_configs[key]
        except KeyError:
            raise

    async def __aenter__(self):
        self.active_session = await self.session_factory().__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.active_session.__aexit__(*args, **kwargs)
        self.active_session = None

    async def _send_request(self, req):
        if self.active_session is None:
            async with self.session_factory() as sess:
                res = await sess.send(req)
        else:
            res = await self.active_session.send(req)
        return res

    async def _refresh_openid_configs(self):
        """
        Downloads fresh openid discovery document and sets it to the current manager.

        OpenID configs are used for both OAuth2 manager and OpenID connect manager.

        Unless this test is failing:

        aiogoogle.tests.integ_online.latest_test_latest_openid_configs(), You shouldn't really need to use this. 
        """
        req = Request("GET", url=OPENID_CONFIGS_DISCOVERY_DOC_URL)
        self.openid_configs = await self._send_request(req)

    @staticmethod
    def authorize(request: Request, user_creds: dict) -> Request:
        if request.headers is None:
            request.headers = {}
        request.headers["Authorization"] = f'Bearer {user_creds["access_token"]}'
        return request

    @staticmethod
    def is_ready(client_creds=None):
        """
        Checks passed ``client_creds`` whether or not the client has enough information to perform OAuth2 Authorization code flow

        Arguments:

            client_creds(aiogoogle.auth.creds.ClientCreds): Client credentials object

        Returns:

            bool: 
        """
        client_creds = client_creds or self.client_creds
        if (
            client_creds.get("client_id")
            and client_creds.get("client_secret")
            and client_creds.get("scopes")
            and isinstance(client_creds["scopes"], (list, tuple))
            and client_creds.get("redirect_uri")
        ):
            return True
        return False

    def authorization_url(
        self,
        client_creds=None,
        state=None,
        access_type=None,
        include_granted_scopes=None,
        login_hint=None,
        prompt=None,
        response_type=AUTH_CODE_RESPONSE_TYPE,
        scopes=None,
    ) -> (str):
        client_creds = client_creds or self.client_creds
        scopes = scopes or client_creds["scopes"]
        scopes = " ".join(client_creds["scopes"])
        uri = (
            self["authorization_endpoint"]
            + f'?redirect_uri={client_creds["redirect_uri"]}&scope={scopes}&'
        )
        for param_name, param in {
            "client_id": client_creds["client_id"],
            "response_type": response_type,
            "state": state,
            "access_type": access_type,
            "include_granted_scopes": json.dumps(include_granted_scopes),
            "login_hint": login_hint,
            "prompt": prompt,
        }.items():
            if param is not None:
                uri += "&"
                uri += parse.urlencode({param_name: param})
        return uri

    async def build_user_creds(
        self, grant, client_creds=None, grant_type=AUTH_CODE_GRANT_TYPE
    ) -> dict:
        client_creds = client_creds or self.client_creds
        request = self._build_user_creds_req(grant, client_creds, grant_type)
        json_res = await self._send_request(request)
        return self._build_user_creds_from_res(json_res)

    def _build_user_creds_req(self, grant, client_creds, grant_type) -> Request:
        data = dict(
            code=grant,
            client_id=client_creds["client_id"],
            client_secret=client_creds["client_secret"],
            redirect_uri=client_creds["redirect_uri"],
            grant_type=grant_type,
        )
        headers = {"content-type": URLENCODED_CONTENT_TYPE}
        method = "POST"
        url = self["token_endpoint"]
        return Request(method, url, headers, data=data)

    def _build_user_creds_from_res(self, json_res):
        scopes = json_res.pop("scope").split(" ")
        user_creds = UserCreds(**json_res, scopes=scopes)
        # Idk why, but sometimes google returns these json params empty
        user_creds["token_uri"] = (
            self["token_endpoint"] if user_creds.get("token_uri") is None else None
        )
        user_creds["token_info_uri"] = (
            TOKEN_INFO_URI if not user_creds.get("token_info_uri") else None
        )
        user_creds["revoke_uri"] = (
            self["revocation_endpoint"] if not user_creds.get("revoke_uri") else None
        )
        user_creds["expires_at"] = self._get_expires_at(user_creds["expires_in"])
        return user_creds

    @staticmethod
    def _get_expires_at(expires_in):
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        # account for clock skew
        expires_at -= datetime.timedelta(seconds=120)
        return expires_at.isoformat()

    @staticmethod
    def authorized_for_method(method, user_creds) -> bool:
        """
        Checks if oauth2 user_creds dict has sufficient scopes for a method call.
        
        .. note:: 
        
            This method doesn't check whether creds are refreshed or valid.

        e.g.

            **Correct:**

            .. code-block:: python3
        
                is_authorized = authorized_for_method(youtube.video.list)
            
            **NOT correct:**

            .. code-block:: python3

                is_authorized = authorized_for_method(youtube.video.list())

            **AND NOT correct:**

            .. code-block:: python3

                is_authorized = authorized_for_method(youtube.videos)


        Arguments:

            method (aiogoogle.resource.Method): Method to be checked

            user_credentials (aiogoogle.auth.creds.UserCreds): User Credentials with scopes item

        Returns:

            bool:

        """
        method_scopes = method["scopes"] or []
        if not method_scopes:
            return True
        if not isinstance(user_creds["scopes"], (list, set, tuple)):
            raise TypeError("Scopes should be an instance of list, set or tuple")
        if set(method_scopes).issubset(set(user_creds["scopes"])):
            return True
        else:
            return False

    async def get_token_info(self, user_creds):
        """
        Gets token info given an access token

        Arguments:

            user_creds (aiogoogle.creds.UserCreds): UserCreds instance with an access token

        Returns:

            dict: Info about the token

        """
        req = self.oauth2_api.tokeninfo(access_token=user_creds.get("access_token"))
        return await self._send_request(req)

    async def get_me_info(self, user_creds):
        """
        Gets information of a user given his access token. User must also be the client.
        (Not sure whether or not that's the main purpose of this endpoint and how it differs from get_user_info.
        If someone can confirm/deny the description above, please edit (or remove) this message and make a pull request)

        Arguments:

            user_creds (aiogoogle.creds.UserCreds): UserCreds instance with an access token

        Returns:

            dict: Info about the user

        Raises:

            aiogoogle.excs.HTTPError:
         """
        req = self.oauth2_api.userinfo.v2.me.get()
        authorized_req = self.authorize(req, user_creds)
        return await self._send_request(authorized_req)

    @staticmethod
    def is_expired(creds) -> bool:
        expires_at = creds["expires_at"]
        if not isinstance(expires_at, datetime.datetime):
            expires_at = datetime.datetime.fromisoformat(expires_at)
        if datetime.datetime.utcnow() >= expires_at:
            return True
        else:
            return False

    async def refresh(self, user_creds, client_creds=None):
        client_creds = client_creds or self.client_creds
        request = self._build_refresh_request(user_creds, client_creds)
        json_res = await self._send_request(request)
        return self._build_user_creds_from_res(json_res)

    def _build_refresh_request(self, user_creds, client_creds):
        data = dict(
            grant_type=REFRESH_GRANT_TYPE,
            client_id=client_creds["client_id"],
            client_secret=(client_creds["client_secret"]),
            refresh_token=(user_creds["refresh_token"]),
        )
        method = "POST"
        headers = {"content-type": URLENCODED_CONTENT_TYPE}
        return Request(method, self["token_endpoint"], headers, data=data)

    def _build_revoke_request(self, user_creds):
        return Request(
            method="POST",
            headers={"content-type": URLENCODED_CONTENT_TYPE},
            url=self["revocation_endpoint"],
            data=dict(token=user_creds["access_token"]),
        )

    async def revoke(self, user_creds):
        request = self._build_revoke_request(user_creds)
        return await self._send_request(request)


class OpenIdConnectManager(Oauth2Manager, AbstractOpenIdConnectManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_user_info(self, user_creds):
        req = self.oauth2_api.userinfo.get()
        authorized_req = self.authorize(req, user_creds)
        return await self._send_request(authorized_req)

    async def get_token_info_jwt(self, user_creds):
        """ get token info using id_token_jwt instead of access_token ``self.get_token_info``
        
        Arguments:
        
            user_creds (aiogoogle.auth.creds.UserCreds): user_creds with id_token_jwt item
            
        Returns:
        
            dict: Information about the token
        """
        req = self.oauth2_api.tokeninfo(id_token=user_creds.get("id_token_jwt"))
        return await self._send_request(req)

    async def _get_openid_certs(self):
        request = Request(
            method="GET",
            url=GOOGLE_OAUTH2_CERTS_URL,
            # url=self['jwks_uri'],  # which is: https://www.googleapis.com/oauth2/v3/certs isn't compatible with google.auth. Falling back to v1
        )
        return await self._send_request(request)

    def authorization_url(
        self,
        client_creds=None,
        nonce=None,
        state=None,
        prompt=None,
        display=None,
        login_hint=None,
        access_type=None,
        include_granted_scopes=None,
        openid_realm=None,
        hd=None,
        response_type=AUTH_CODE_RESPONSE_TYPE,
        scopes=None,
    ):
        client_creds = client_creds or self.client_creds
        if nonce is None:
            raise TypeError("Nonce is required")
        scopes = scopes or client_creds["scopes"]
        scopes = " ".join(scopes)
        uri = (
            self["authorization_endpoint"]
            + f'?redirect_uri={client_creds["redirect_uri"]}&scope={scopes}&'
        )
        for param_name, param in {
            "client_id": client_creds["client_id"],
            "nonce": nonce,
            "display": display,
            "openid.realm": openid_realm,
            "hd": hd,
            "response_type": response_type,
            "state": state,
            "access_type": access_type,
            "include_granted_scopes": json.dumps(include_granted_scopes),
            "login_hint": login_hint,
            "prompt": prompt,
        }.items():
            if param is not None:
                uri += "&"
                uri += parse.urlencode({param_name: param})
        return uri

    async def build_user_creds(
        self,
        grant,
        client_creds=None,
        grant_type=AUTH_CODE_GRANT_TYPE,
        nonce=None,
        hd=None,
        verify=True,
    ):
        client_creds = client_creds or self.client_creds
        user_creds = await super().build_user_creds(
            grant, client_creds, grant_type=grant_type
        )
        user_creds["id_token_jwt"] = user_creds["id_token"]
        if verify is False:
            user_creds["id_token"] = jwt.decode(
                user_creds["id_token_jwt"], verify=False
            )
        else:
            user_creds["id_token"] = await self.decode_and_validate(
                user_creds["id_token_jwt"], client_creds["client_id"], nonce, hd
            )
        return user_creds

    async def decode_and_validate(
        self, id_token_jwt, client_id=None, nonce=None, hd=None
    ):
        certs = await self._get_openid_certs()  # refreshed once a day-ish
        # Verify ID token is signed by google
        try:
            id_token = jwt.decode(id_token_jwt, certs=certs, verify=True)
        except ValueError as e:
            raise AuthError(e)
        # Verify iss (The Issuer Identifier for the Issuer of the response) is https://accounts.google.com
        if id_token["iss"] != DEFAULT_ISS:
            raise AuthError(
                f"Invalid issuer, got: {id_token['iss']}, expected: {DEFAULT_ISS}"
            )
        if nonce is not None:
            if nonce != id_token["nonce"]:
                raise AuthError("Provided nonce does not match the encoded nonce")
        if hd is not None:
            if hd != id_token["hd"]:
                raise AuthError(
                    f"Hosted domains do not match, got: {id_token['hd']}, expected: {hd}"
                )
        # verify expiry 'exp' (google.jwt handles that)
        # verify audience
        if client_id is not None:
            if id_token["aud"] != client_id:
                raise AuthError(
                    f"Invalid audience. Got: {id_token['aud']} expected: {client_id}"
                )
        return id_token

    async def build_user_creds_jwt_grant(self, assertion, token_uri):
        """
        Implements the JWT Profile for OAuth 2.0 Authorization Grants.

        Args:

            assertion (str):

                * A single id_token_jwt

            token_uri (str):

                * Token URI of your authorization server

        Returns:
            
            aiogoogle.auth.creds.UserCreds:

        Raises:
            
            aiogoogle.excs.AuthError: 

        .. _rfc7523 section 4: https://tools.ietf.org/html/rfc7523#section-4 (Section 2.1 for an example: https://tools.ietf.org/html/rfc7523#section-2.1)
        """
        data = {"assertion": assertion, "grant_type": JWT_GRANT_TYPE}
        req = Request(method="POST", url=token_uri, data=data)
        json_res = await self._send_request(req)
        user_creds = self._build_user_creds_from_res(json_res)
        if user_creds.get("id_token"):  # Google specific (Not RFC compliant)
            user_creds["id_token"] = jwt.decode(
                user_creds["id_token_jwt"], verify=False
            )
        return user_creds

    async def build_user_creds_jwt_auth(self, assertion, token_uri):
        """https://tools.ietf.org/html/rfc7523#section-2.2 """
        raise NotImplementedError
