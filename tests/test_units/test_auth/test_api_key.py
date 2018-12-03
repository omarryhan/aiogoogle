from aiogoogle.auth.managers import ApiKeyManager
from aiogoogle.models import Request
from aiogoogle.resource import GoogleAPI
import pytest


@pytest.fixture
def manager():
    return ApiKeyManager()

@pytest.fixture
def key1():
    return 'asdasdasidajosnoqwndoasfnwuiefn'

@pytest.fixture
def key2():
    return 'asjdaosdniaurn3uh2873he9has9dhASDQ(Dasd'


def test_google_api_is_functional(manager, create_api, key1):
    api = create_api('urlshortener', 'v1')
    request_with_key = api.url.get(key=key1, shortUrl='asdasd', validate=False)
    assert key1 in request_with_key.url

#--- tests begin here

def test_doesnt_add_key_when_existing(manager, create_api, key1):
    api = create_api('urlshortener', 'v1')
    request_with_key = api.url.get(key=key1, shortUrl='asdasd', validate=False)
    new_request = manager.authorize(request_with_key, key1)
    assert request_with_key.url == new_request.url

def test_adds_key_to_url_with_query(manager, create_api, key1):
    api = create_api('urlshortener', 'v1')
    request_with_key = api.url.get(shortUrl='asdasd', key=key1)  # Must be kept in this order for this test to pass
    request_without_key = api.url.get(shortUrl='asdasd')
    request_without_key_authorized = manager.authorize(request_without_key, key1)
    assert request_without_key_authorized.url == request_with_key.url

def test_adds_key_to_url_without_query(manager, key1):
    url = 'https://example.com/api'
    req = Request(url=url)
    request_with_key = manager.authorize(req, key1)
    assert request_with_key.url == url + '?key=' + key1

def test_adds_key_to_url_without_query_and_with_slash(manager, key1):
    url = 'https://example.com/api/'
    req = Request(url=url)
    request_with_key = manager.authorize(req, key1)
    assert request_with_key.url == url[:-1] + '?key=' + key1
    
    