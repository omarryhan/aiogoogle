import pytest

import pprint
from aiogoogle.resource import Resource, GoogleAPI, Method
from aiogoogle import Aiogoogle
from ..globals import SOME_APIS


@pytest.mark.parametrize('name,version', SOME_APIS)
def test_getitem(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert api['name'] == discovery_document.get('name')
    assert api['version'] == discovery_document.get('version')
    assert api['auth'] == discovery_document.get('auth')

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_properties(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    assert len(api) == len(discovery_document.get('resources'))
    assert (name in str(api)) or (discovery_document.get('title') in str(api))
    assert (version in str(api)) or (discovery_document.get('title') in str(api))

def test_user_authorized_for_method(open_discovery_document):
    discovery_document = open_discovery_document('youtube', 'v3')
    youtube = GoogleAPI(discovery_document=discovery_document)
    aiogoogle = Aiogoogle()
    assert aiogoogle.user_authorized_for_method(
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

    assert aiogoogle.user_authorized_for_method(
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

    assert aiogoogle.user_authorized_for_method(
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

    assert aiogoogle.user_authorized_for_method(
        method=youtube.videos.list,
        user_creds={
            'scopes': []
        }
    ) is False

    with pytest.raises(TypeError) as e:
        aiogoogle.user_authorized_for_method(
            method=youtube.videos.list,
            user_creds={
                'scopes': None
            }
        )
        assert str(e) == 'Scopes should be an instance of list, set or tuple'
