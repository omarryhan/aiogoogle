import pytest

from aiogoogle import Aiogoogle
from ..test_globals import ALL_APIS

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
