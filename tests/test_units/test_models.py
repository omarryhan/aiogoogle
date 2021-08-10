# TODO: Test request add query param
# TODO: Test request rm query param
# TODO: Test Request.from response
# TODO: Test next page generator
# TODO: Test response.__call__ returns pagination gen
# TODO: Test next_page returns a valid request
import asyncio
from unittest.mock import MagicMock

import pytest

from aiogoogle.models import Request, MediaUpload
from aiogoogle.excs import ValidationError


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


add_query_params = (
    ("https://example.com", {'foo': 'bar'}, 'https://example.com?foo=bar'),
    ("https://example.com/foo", {'bar': 'baz'}, 'https://example.com/foo?bar=baz'),
    ("https://example.com/", {'bar': 'baz'}, 'https://example.com?bar=baz'),
    ("https://example.com/foo?bar=baz", {'idk': 'fuuu'}, 'https://example.com/foo?bar=baz&idk=fuuu')
)


@pytest.mark.parametrize("url, params, result", add_query_params)
def test_request_add_query_param(url, params, result):
    r = Request(url=url)
    r._add_query_param(params)
    assert r.url == result


def noop(*args, **kwargs):
    return


@pytest.mark.asyncio
async def test_media_upload_bytes_aiter():
    body = bytes(101)
    mu = MediaUpload(body, chunk_size=10)
    chunks = [chunk async for chunk in mu.aiter_file(noop)]
    assert len(chunks) == 11
    joined = b"".join(chunks)
    assert body == joined


@pytest.mark.asyncio
async def test_media_upload_bytes_read():
    body = bytes(101)
    mu = MediaUpload(body)
    assert await mu.read_file(noop) == body


@pytest.mark.asyncio
async def test_media_upload_bytes_validation():
    body = bytes(101)
    mu = MediaUpload(body, max_size=10)
    with pytest.raises(ValidationError):
        await mu.run_validation(noop)

    mu = MediaUpload(body, max_size=200)
    await mu.run_validation(noop)


@pytest.mark.asyncio
async def test_media_upload_aiter():
    file_path = "test"
    mu = MediaUpload(file_path, chunk_size=10)
    aiter_func = MagicMock(return_value=AsyncIterator(range(5)))
    chunks = [chunk async for chunk in mu.aiter_file(aiter_func)]
    aiter_func.assert_called_once_with(file_path, 10)
    assert len(chunks) == 5


@pytest.mark.asyncio
async def test_media_upload_read():
    file_path = "test"
    mu = MediaUpload(file_path)
    read_func = MagicMock(return_value=async_return(None))
    await mu.read_file(read_func)
    read_func.assert_called_once_with(file_path)


@pytest.mark.asyncio
async def test_media_upload_validation():
    file_path = "test"
    mu = MediaUpload(file_path, max_size=10)
    size_func = MagicMock(return_value=async_return(100))
    with pytest.raises(ValidationError):
        await mu.run_validation(size_func)

    mu = MediaUpload(file_path, max_size=200)
    await mu.run_validation(size_func)
