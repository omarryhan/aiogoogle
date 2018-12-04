import pytest

from aiogoogle import Aiogoogle
from ..test_globals import ALL_APIS
from aiogoogle.auth.managers import OPENID_CONFIGS_DISCOVERY_DOC_URL as openid_url
from aiogoogle.auth.data import WELLKNOWN_OPENID_CONFIGS as currunt_openid_configs
from aiohttp import ClientSession

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', ALL_APIS)
async def test_download_aiogoogle(name, version):
    aiogoogle = Aiogoogle()
    google_api = await aiogoogle.discover(name, version)
    assert google_api.discovery_document

@pytest.mark.asyncio
@pytest.mark.parametrize('name,version', ALL_APIS)
async def test_download_aiogoogle_without_version(name, version):
    aiogoogle = Aiogoogle()
    google_api = await aiogoogle.discover(name)
    assert google_api.discovery_document['name'] == name
    assert google_api.discovery_document['version'] == version

@pytest.mark.asyncio
async def test_oauth2_manager_api_is_latest_version():
    CURRENT_OAUTH2_API_VERSION = 2
    async with Aiogoogle() as google:
        oauth2_apis_list = await google.list_api('oauth2')
    apis = oauth2_apis_list['items']
    versions_available = [int(api['version'][-1:]) for api in apis]
    for version in versions_available:
        assert CURRENT_OAUTH2_API_VERSION >= version

@pytest.mark.asyncio
async def test_latest_openid_configs():
    async with ClientSession() as sess:
        new_configs_res = await sess.get(openid_url)
        new_configs = await new_configs_res.json()
        assert new_configs == currunt_openid_configs