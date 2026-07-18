import sys
from unittest.mock import patch
from aiogoogle.client import Aiogoogle, DISCOVERY_SERVICE_V1_DISCOVERY_DOC
from aiogoogle.excs import HTTPError
import pytest


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="requires python3.8"
)
@pytest.mark.asyncio
async def test_fetch_api_discovery_doc_via_google_discovery_service_v2():
    from unittest.mock import AsyncMock

    expected = "https://drivelabels.googleapis.com/$discovery/rest?version=v2beta"
    mock_send_unauthorized_requests = AsyncMock(
        name="aiogoogle_client_send_unauthorized_requests",
        return_value=DISCOVERY_SERVICE_V1_DISCOVERY_DOC
    )

    with patch("socket.socket.connect") as mock_network_connection:
        # Don't allow this unittest to make any network connections by accident
        mock_network_connection.side_effect = Exception(
            "An attempt was made to hit the network"
        )
        # Mock fetching a Google API discovery doc with a custom endpoint URL
        async with Aiogoogle() as google:
            google.as_anon = mock_send_unauthorized_requests
            # Create the specified Google API
            await google.discover(
                "drivelabels",
                "v2beta",
                disco_doc_ver=2
            )

        # Validate that the correct Google endpoint would have been called
        google_api_request = mock_send_unauthorized_requests.await_args[0][0]
        google_api_request.url == expected


@pytest.mark.parametrize("disco_doc_ver", [None, 2])
@pytest.mark.asyncio
async def test_discover_propagates_http_error(disco_doc_ver):
    req = object()
    res = object()
    error = HTTPError("discovery failed", req=req, res=res)

    async def raise_http_error(request):
        raise error

    google = Aiogoogle()
    google.as_anon = raise_http_error

    with pytest.raises(HTTPError) as raised:
        await google.discover("drive", "v3", disco_doc_ver=disco_doc_ver)

    assert raised.value is error
    assert raised.value.req is req
    assert raised.value.res is res
    assert ("disco_doc_ver=2" in str(raised.value)) is (disco_doc_ver is None)


@pytest.mark.asyncio
async def test_discover_propagates_unrelated_value_error():
    error = ValueError("unrelated error")

    async def raise_value_error(request):
        raise error

    google = Aiogoogle()
    google.as_anon = raise_value_error

    with pytest.raises(ValueError) as raised:
        await google.discover("drive", "v3")

    assert raised.value is error
    assert str(raised.value) == "unrelated error"
