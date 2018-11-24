'''
.. note::

    - These are the default auth managers. They won't perform any file io.
    - If you want auth managers with file io capabilities, then you'll have to 
    implement AbstractAuthManager's interface or inherent from this module's classes.
    - Creds will always be an instance of dict in order to be easily serialized for io operations
'''


__all__ = [
    'Oauth2Manager',
    'ApiKeyManager'
]


from urllib import parse

from .abc import AbstractOAuth2Manager, AbstractAPIKeyManager
from .creds import UserCreds, ClientCreds
from .utils import _create_secret
from ..models import Request



class Oauth2Manager(AbstractOAuth2Manager):

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.active_session = None

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

    def is_expired(self, creds: dict) -> bool:
        pass

    async def refresh(self, *user_creds, client_creds=None) -> dict:
        pass

    def build_auth_uri(self, client_creds, user_creds=None, state=None) -> (str, dict):
        if user_creds is None:
            user_creds = UserCreds()
        if state is None:
            state = _create_secret(32)
        pass

    async def build_user_creds(self, grant, client_creds, user_creds=None, verify_state=True) -> dict:
        pass

class ApiKeyManager(AbstractAPIKeyManager):

    def authorize(self, request, key: str) -> Request:
        url = request.url
        # TODO: Do this using urllib

        # TODO:
        # if url has fragment, seperate it
        # fragment = ...
        # url -= fragment

        if '?' not in url:
            if url.endswith('/'):
                url = url[:-1]
            url += '?'
        else:
            url += '&'

        url += f'key={key}'

        # TODO:
        # readd fragment
        # url += fragment

        request.url = url
        return request
