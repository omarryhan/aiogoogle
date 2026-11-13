import json
from socket import socket

import pytest
from aiohttp import web

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
            "supportsMediaUpload": True,
            "mediaUpload": {
                "accept": ["*/*"],
                "protocols": {"simple": {"multipart": True, "path": "files"}},
            },
        },
        global_parameters={},
        schemas={},
        batch_path=root_url + "batch",
        service_path="drive/v3/",
        root_url=root_url,
        validate=False,
    )


async def _aiter_content():
    yield CONTENT[:6]
    yield CONTENT[6:]


@pytest.mark.parametrize(
    "kwargs, upload_type",
    [
        ({"upload_file": "FILE"}, "media"),
        ({"pipe_from": "PIPE"}, "media"),
        ({"upload_file": "FILE", "json": {"name": "report.txt"}}, "multipart"),
        ({"pipe_from": "PIPE", "json": {"name": "report.txt"}}, "multipart"),
    ],
)
@pytest.mark.asyncio
async def test_upload_body_matches_upload_type(tmp_path, kwargs, upload_type):
    received = {}

    async def handler(request):
        received["upload_type"] = request.query.get("uploadType")
        received["content_type"] = request.content_type
        received["body"] = await request.read()
        return web.json_response({"id": "1"})

    app = web.Application()
    app.router.add_post("/upload/drive/v3/files", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    await web.SockSite(runner, sock).start()

    path = tmp_path / "report.txt"
    path.write_bytes(CONTENT)
    kwargs = dict(kwargs)
    if kwargs.get("upload_file") == "FILE":
        kwargs["upload_file"] = str(path)
    if kwargs.get("pipe_from") == "PIPE":
        kwargs["pipe_from"] = _aiter_content()

    req = _upload_method(f"http://127.0.0.1:{port}/")(**kwargs)
    try:
        async with AiohttpSession() as session:
            await session.send(req, full_res=True)
    finally:
        await runner.cleanup()

    assert received["upload_type"] == upload_type
    if upload_type == "media":
        assert received["body"] == CONTENT
    else:
        assert received["content_type"] == "multipart/related"
        metadata, media = received["body"].split(b"\r\n\r\n", 2)[1:]
        assert json.loads(metadata.split(b"\r\n")[0]) == {"name": "report.txt"}
        assert media.startswith(CONTENT)
