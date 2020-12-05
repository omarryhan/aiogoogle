# TODO: Test request add query param
# TODO: Test request rm query param
# TODO: Test Request.from response
# TODO: Test next page generator
# TODO: Test response.__call__ returns pagination gen
# TODO: Test next_page returns a valid request
from aiogoogle.models import Request


def test_request_add_query_param():
    r = Request(url="https://example.com")
    r._add_query_param({'foo': 'bar'})
    assert r.url == 'https://example.com?foo=bar'


def test_request_add_query_param1():
    r = Request(url="https://example.com/foo")
    r._add_query_param({'bar': 'baz'})
    assert r.url == 'https://example.com/foo?bar=baz'


def test_request_add_query_param2():
    r = Request(url="https://example.com/")
    r._add_query_param({'bar': 'baz'})
    assert r.url == 'https://example.com?bar=baz'


def test_request_add_query_param3():
    r = Request(url="https://example.com/foo?bar=baz")
    r._add_query_param({'idk': 'fuuu'})
    assert r.url == 'https://example.com/foo?bar=baz&idk=fuuu'
