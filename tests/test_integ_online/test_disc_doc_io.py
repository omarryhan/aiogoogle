import pytest

from aiogoogle import Aiogoogle
from aiogoogle.auth.managers import OPENID_CONFIGS_DISCOVERY_DOC_URL as openid_url
from aiogoogle.auth.data import WELLKNOWN_OPENID_CONFIGS as currunt_openid_configs
from aiohttp import ClientSession


@pytest.mark.asyncio
async def test_oauth2_manager_api_is_latest_version():
    CURRENT_OAUTH2_API_VERSION = 2
    async with Aiogoogle() as google:
        oauth2_apis_list = await google.list_api("oauth2")
    apis = oauth2_apis_list["items"]
    versions_available = [int(api["version"][-1:]) for api in apis]
    for version in versions_available:
        assert CURRENT_OAUTH2_API_VERSION >= version


@pytest.mark.asyncio
async def test_latest_openid_configs():
    async with ClientSession() as sess:
        new_configs_res = await sess.get(openid_url)
        new_configs = await new_configs_res.json()

        new_config_keys = list(new_configs.keys())
        currunt_openid_configs_keys = list(currunt_openid_configs.keys())

        new_config_keys.sort()
        currunt_openid_configs_keys.sort()

        assert new_config_keys == currunt_openid_configs_keys
        assert len(new_config_keys) == len(currunt_openid_configs_keys)
        for k in new_config_keys:
            assert new_configs[k] == currunt_openid_configs[k]
