from aiogoogle.auth.managers import Oauth2Manager
from aiogoogle.models import Request
from aiogoogle.resource import GoogleAPI
from aiogoogle.client import Aiogoogle
from aiogoogle.sessions.aiohttp_session import AiohttpSession
import pytest


@pytest.fixture
def manager():
    return Oauth2Manager(AiohttpSession)

def test_oauth2_manager_has_valid_oauth2_api(manager):
    assert isinstance(manager.oauth2_api, GoogleAPI)

def test_authorize(manager):
    access_name = 'access'
    unauth_req = Request()
    user_creds = {
        'access_token': access_name
    }

    auth_req = manager.authorize(unauth_req, user_creds)
    assert auth_req.headers['Authorization'] == 'Bearer ' + access_name

    with pytest.raises(KeyError):
        auth_req = manager.authorize(unauth_req, {})

def test_is_ready(manager):
    # client creds must have: client secret, client id, scopes, redirect uri
    ready_creds = {
        'client_secret': 'asasd',
        'client_id': 'casas',
        'scopes': ['asd', 'asd'],
        'redirect_uri': 'asdasd'
    }

    unready_creds = [
        {
            'client_secret': 'asasd',
            'scopes': ['asd', 'asd'],
            'redirect_uri': 'asdasd'
        },
        {
            'client_secret': 'asasd',
            'client_id': 'casas',
            'scopes': ['asd', 'asd'],
        },
        {
            'client_id': 'casas',
            'scopes': ['asd', 'asd'],
            'redirect_uri': 'asdasd'
        },
        {
            'client_secret': 'asasd',
            'client_id': 'casas',
            'scopes': 'asd',
            'redirect_uri': 'asdasd'
        },
        {
            'client_secret': 'asasd',
            'client_id': 'casas',
            'scopes': {'asd': 'asd'},
            'redirect_uri': 'asdasd'
        },
    ]

    assert manager.is_ready(ready_creds) is True

    for unready_creds_ in unready_creds:
        assert manager.is_ready(unready_creds_) is False

def test_authorization_url():
    # TODO:
    pass

def test_build_user_creds_req():
    # TODO:
    pass

def test_build_user_creds_from_res():
    # TODO:
    pass

def test_get_expires_at():
    # TODO:
    pass

def test_is_expired():
    # TODO:
    pass

def test_build_refresh_request():
    # TODO:
    pass

def test_build_revoke_request():
    # TODO:
    pass

@pytest.mark.asyncio
async def test_oauth2_manager_api_is_latest_version(manager):

    CURRENT_OAUTH2_API_VERSION = 2

    async with Aiogoogle() as google:
        oauth2_apis_list = await google.list_api('oauth2')

    apis = oauth2_apis_list['items']

    versions_available = [int(api['version'][-1:]) for api in apis]

    for version in versions_available:
        assert CURRENT_OAUTH2_API_VERSION >= version

def test_user_authorized_for_method(open_discovery_document):
    discovery_document = open_discovery_document('youtube', 'v3')
    youtube = GoogleAPI(discovery_document=discovery_document)
    aiogoogle = Aiogoogle()
    assert aiogoogle.oauth2.authorized_for_method(
        method=youtube.videos.list,
        user_creds={
            'scopes': [
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ]
        }
    ) is True

    assert aiogoogle.oauth2.authorized_for_method(
        method=youtube.videos.list,
        user_creds={
            'scopes': [
                #"https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ]
        }
    ) is False

    assert aiogoogle.oauth2.authorized_for_method(
        method=youtube.videos.list,
        user_creds={
            'scopes': [
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner",
                "useless_scope"
            ]
        }
    ) is True

    assert aiogoogle.oauth2.authorized_for_method(
        method=youtube.videos.list,
        user_creds={
            'scopes': []
        }
    ) is False

    with pytest.raises(TypeError) as e:
        aiogoogle.oauth2.authorized_for_method(
            method=youtube.videos.list,
            user_creds={
                'scopes': None
            }
        )
        assert str(e) == 'Scopes should be an instance of list, set or tuple'
