import json
from socket import socket

import pytest
from aiohttp import web

from aiogoogle.models import MediaUpload
from aiogoogle.resource import Method
from aiogoogle.sessions.aiohttp_session import AiohttpSession

CONTENT = b"report content"


def _upload_method(root_url):
    return Method(
        name="create",
        method_specs={
            "path": "files",
            "httpMethod": "POST",
            "parameters": {},
            "request": {"type": "object", "properties": {"name": {"type": "string"}}},
            "supportsMediaUpload": True,
            "mediaUpload": {
                "accept": ["*/*"],
                "maxSize": "1MB",
                "protocols": {"simple": {"multipart": True, "path": "files"}},
            },
        },
        global_parameters={},
        schemas={},
        batch_path=root_url + "batch",
        service_path="drive/v3/",
        root_url=root_url,
        # Validation on: a pipe_from stream must pass the maxSize check without a known size
        validate=True,
    )


async def _aiter_content():
    yield CONTENT[:6]
    yield CONTENT[6:]


class _AsyncReader:
    async def read(self):
        return CONTENT


class _SyncReader:
    def read(self):
        return CONTENT


SOURCES = {
    "file": lambda path: {"upload_file": str(path)},
    "bytes": lambda path: {"upload_file": CONTENT},
    "async_iterable": lambda path: {"pipe_from": _aiter_content()},
    "async_read": lambda path: {"pipe_from": _AsyncReader()},
    "sync_read": lambda path: {"pipe_from": _SyncReader()},
}


@pytest.mark.parametrize("source", list(SOURCES))
@pytest.mark.parametrize("upload_type", ["media", "multipart"])
@pytest.mark.asyncio
async def test_upload_body_matches_upload_type(tmp_path, monkeypatch, source, upload_type):
    received = {}

    async def read_whole_file(self, read_func):
        raise AssertionError("uploads must be streamed, not read into memory")

    monkeypatch.setattr(MediaUpload, "read_file", read_whole_file)

    async def handler(request):
        received["upload_type"] = request.query.get("uploadType")
        received["content_type"] = request.content_type
        received["content_length"] = request.headers.get("Content-Length")
        received["body"] = await request.read()
        return web.json_response({"id": "1"})

    app = web.Application()
    app.router.add_post("/upload/drive/v3/files", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    try:
        sock = socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        await web.SockSite(runner, sock).start()

        path = tmp_path / "report.txt"
        path.write_bytes(CONTENT)
        kwargs = SOURCES[source](path)
        if upload_type == "multipart":
            kwargs["json"] = {"name": "report.txt"}

        req = _upload_method(f"http://127.0.0.1:{port}/")(**kwargs)
        async with AiohttpSession() as session:
            await session.send(req, full_res=True)
    finally:
        await runner.cleanup()

    assert received["upload_type"] == upload_type
    if upload_type == "media":
        assert received["body"] == CONTENT
        if source in ("file", "bytes"):
            # Sized sources keep Content-Length instead of a chunked body
            assert received["content_length"] == str(len(CONTENT))
    else:
        assert received["content_type"] == "multipart/related"
        metadata, media = received["body"].split(b"\r\n\r\n", 2)[1:]
        assert json.loads(metadata.split(b"\r\n")[0]) == {"name": "report.txt"}
        assert media.startswith(CONTENT)
