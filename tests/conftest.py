import pytest


@pytest.fixture('session')
def youtube_v3_discovery_doc_url():
    return "https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest"