from socket import socket
from unittest.mock import AsyncMock

import pytest
from aiohttp import web

from aiogoogle.excs import HTTPError
from aiogoogle.models import MediaDownload, Request
from aiogoogle.sessions.aiohttp_session import AiohttpSession


@pytest.mark.parametrize("status", [401, 403, 500])
@pytest.mark.parametrize("destination", ["pipe", "file"])
@pytest.mark.parametrize("raise_for_status", [True, False])
@pytest.mark.asyncio
async def test_download_error_is_parsed_not_written(tmp_path, status, destination, raise_for_status):
    error = {"error": {"code": status, "message": "Export denied", "errors": [{"reason": "exportSizeLimitExceeded"}]}}

    async def handler(request):
        return web.json_response(error, status=status)

    app = web.Application()
    app.router.add_get("/export", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    await web.SockSite(runner, sock).start()
    target = tmp_path / "report.xlsx"
    target.write_bytes(b"existing report")
    sink = AsyncMock()
    download = MediaDownload(pipe_to=sink) if destination == "pipe" else MediaDownload(file_path=str(target))
    req = Request(method="GET", url=f"http://127.0.0.1:{port}/export", media_download=download)
    try:
        async with AiohttpSession() as session:
            if raise_for_status:
                with pytest.raises(HTTPError) as raised:
                    await session.send(req, full_res=True)
                response = raised.value.res
                assert "exportSizeLimitExceeded" in str(raised.value)
            else:
                response = await session.send(req, full_res=True, raise_for_status=False)
            assert response.json == error
            assert response.status_code == status
            sink.write.assert_not_awaited()
            assert target.read_bytes() == b"existing report"
    finally:
        await runner.cleanup()


@pytest.mark.parametrize("destination", ["pipe", "file"])
@pytest.mark.asyncio
async def test_successful_download_still_writes(tmp_path, destination):
    body = b"spreadsheet content"

    async def handler(request):
        return web.Response(body=body, content_type="application/octet-stream")

    app = web.Application()
    app.router.add_get("/export", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    await web.SockSite(runner, sock).start()
    target = tmp_path / "report.xlsx"
    sink = AsyncMock()
    download = MediaDownload(pipe_to=sink, chunk_size=4) if destination == "pipe" else MediaDownload(file_path=str(target), chunk_size=4)
    req = Request(method="GET", url=f"http://127.0.0.1:{port}/export", media_download=download)
    try:
        async with AiohttpSession() as session:
            response = await session.send(req, full_res=True)
        assert response.status_code == 200
        if destination == "pipe":
            assert b"".join(call.args[0] for call in sink.write.await_args_list) == body
        else:
            assert target.read_bytes() == body
    finally:
        await runner.cleanup()


@pytest.mark.parametrize("destination", ["pipe", "file"])
@pytest.mark.asyncio
async def test_non_json_download_error_does_not_create_output(tmp_path, destination):
    async def handler(request):
        return web.Response(text="Upstream unavailable", status=503)

    app = web.Application()
    app.router.add_get("/export", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    sock = socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    await web.SockSite(runner, sock).start()
    target = tmp_path / "new-report.xlsx"
    sink = AsyncMock()
    download = MediaDownload(pipe_to=sink) if destination == "pipe" else MediaDownload(file_path=str(target))
    req = Request(method="GET", url=f"http://127.0.0.1:{port}/export", media_download=download)
    try:
        async with AiohttpSession() as session:
            with pytest.raises(HTTPError) as raised:
                await session.send(req, full_res=True)
        assert raised.value.res.data == "Upstream unavailable"
        sink.write.assert_not_awaited()
        assert not target.exists()
    finally:
        await runner.cleanup()
