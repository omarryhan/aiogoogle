import sys
from unittest.mock import patch
from aiogoogle.client import Aiogoogle, DISCOVERY_SERVICE_V1_DISCOVERY_DOC
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
