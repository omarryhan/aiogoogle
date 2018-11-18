import pytest

import pprint
from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod
from ...globals import SOME_APIS


def test_discovery_client():
    DiscoveryClient()

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_discovery_doc_setter(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    assert client.name == discovery_document.get('name')
    assert client.version == discovery_document.get('version')
    assert getattr(client, 'auth', None) == discovery_document.get('auth')
    assert isinstance(client.resources, Resources)

@pytest.mark.parametrize('name,version', SOME_APIS)
def test_properties(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    client = DiscoveryClient(discovery_document=discovery_document)
    assert client.name == discovery_document.get('name')
    assert client.version == discovery_document.get('version')
    assert len(client) == len(discovery_document.get('resources'))
    assert (name in str(client)) or (discovery_document.get('title') in str(client))
    assert (version in str(client)) or (discovery_document.get('title') in str(client))

def test_user_authorized_for_method(open_discovery_document):
    discovery_document = open_discovery_document('youtube', 'v3')
    client = DiscoveryClient(discovery_document=discovery_document)
    assert client.user_authorized_for_method(
        resource_method=client.resources.videos.list,
        user_creds={
            'scopes': [
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ]
        }
    ) is True

    assert client.user_authorized_for_method(
        resource_method=client.resources.videos.list,
        user_creds={
            'scopes': [
                #"https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ]
        }
    ) is False

    assert client.user_authorized_for_method(
        resource_method=client.resources.videos.list,
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

    assert client.user_authorized_for_method(
        resource_method=client.resources.videos.list,
        user_creds={
            'scopes': []
        }
    ) is False

    with pytest.raises(TypeError) as e:
        client.user_authorized_for_method(
            resource_method=client.resources.videos.list,
            user_creds={
                'scopes': None
            }
        )
        assert str(e) == 'Scopes should be an instance of list, set or tuple'
