__all__ = ["AiohttpSession"]

import asyncio
from json import JSONDecodeError

from aiohttp import ClientSession, MultipartWriter
from aiohttp.client_exceptions import ContentTypeError
import aiofiles
from aiofiles import os as async_os
import async_timeout

from ..models import Response
from .abc import AbstractSession
from ..excs import ValidationError


async def _get_file_size(full_file_path):
    stat = await async_os.stat(full_file_path)
    return stat.st_size


async def _aiter_file(file_name, chunk_size):
    """ Async file generator """
    async with aiofiles.open(file_name, "rb") as f:
        chunk = await f.read(chunk_size)
        while chunk:
            yield chunk
            chunk = await f.read(chunk_size)


class AiohttpSession(ClientSession, AbstractSession):
    async def send(
        self,
        *requests,
        timeout=None,
        full_res=False,
        raise_for_status=True,
        session_factory=None,
    ):
        async def resolve_response(request, response):
            data = None
            json = None
            download_file = None
            upload_file = None

            # If downloading file:
            if request.media_download:
                chunk_size = request.media_download.chunk_size
                download_file = request.media_download.file_path
                async with aiofiles.open(download_file, "wb+") as f:
                    async for line in response.content.iter_chunked(chunk_size):
                        await f.write(line)
            else:
                if response.status != 204:  # If no (no content)
                    try:
                        json = await response.json()
                    except (JSONDecodeError, ContentTypeError):
                        try:
                            data = await response.text()
                        except ContentTypeError:
                            try:
                                data = await response.read()
                            except ContentTypeError:
                                data = None

            if request.media_upload:
                upload_file = request.media_upload.file_path

            return Response(
                url=str(response.url),
                headers=response.headers,
                status_code=response.status,
                json=json,
                data=data,
                reason=response.reason if getattr(response, "reason") else None,
                req=request,
                download_file=download_file,
                upload_file=upload_file,
                session_factory=session_factory,
            )

        async def fire_request(request):
            request.headers["Accept-Encoding"] = "gzip"
            request.headers["User-Agent"] = "Aiogoogle Aiohttp (gzip)"
            if request.media_upload:
                # Validate
                if (
                    request.media_upload.validate is True
                    and request.media_upload.max_size is not None
                ):
                    size = await _get_file_size(request.media_upload.file_path)
                    max_size = request.media_upload.max_size
                    if size > max_size:
                        raise ValidationError(
                            f'"{request.media_upload.file_path}" has a size of {size/1000}KB. Max upload size for this endpoint is: {max_size/1000}KB.'
                        )

                # If multipart pass a file async generator
                if request.media_upload.multipart is True:
                    with MultipartWriter('mixed') as mpwriter:
                        mpwriter.append(
                            _aiter_file(
                                request.media_upload.file_path,
                                request.media_upload.chunk_size
                            ),
                            headers={"Content-Type": request.upload_file_content_type} if request.upload_file_content_type else None
                        )
                        if request.json:
                            mpwriter.append_json(request.json)

                        req_content_type = (request.upload_file_content_type or "multipart/related") if not request.json else "multipart/related"

                        request.headers.update({"Content-Type": f"{req_content_type}; boundary={mpwriter.boundary}"})

                        # Aiohttp already handles this for us. Also the line below doesn't work. dk why.
                        # request.headers.update({"Content-Length": str(size)})

                        return await self.request(
                            method=request.method,
                            url=request.media_upload.upload_path,
                            headers=request.headers,
                            data=mpwriter,
                            timeout=request.timeout,
                            verify_ssl=request._verify_ssl,
                        )
                # Else load file to memory and send
                else:
                    async with aiofiles.open(
                        request.media_upload.file_path, "rb"
                    ) as file:
                        read_file = await file.read()
                        if request.upload_file_content_type:
                            request.headers.update({"Content-Type": request.upload_file_content_type})
                        return await self.request(
                            method=request.method,
                            url=request.media_upload.upload_path,
                            headers=request.headers,
                            data=read_file,
                            json=request.json,
                            timeout=request.timeout,
                            verify_ssl=request._verify_ssl,
                        )
            # Else, if no file upload
            else:
                return await self.request(
                    method=request.method,
                    url=request.url,
                    headers=request.headers,
                    data=request.data,
                    json=request.json,
                    timeout=request.timeout,
                    verify_ssl=request._verify_ssl,
                )

        # ----------------- send sequence ------------------#
        async def get_response(request):
            response = await fire_request(request)
            response = await resolve_response(request, response)
            if raise_for_status is True:
                response.raise_for_status()
            return response

        async def get_content(request):
            response = await get_response(request)
            return response.content

        # ----------------- /send sequence ------------------#

        async def schedule_tasks():
            if full_res is True:
                tasks = [
                    asyncio.ensure_future(get_response(request)) for request in requests
                ]
            else:
                tasks = [
                    asyncio.ensure_future(get_content(request)) for request in requests
                ]
            return await asyncio.gather(*tasks, return_exceptions=False)

        session_factory = self.__class__ if session_factory is None else session_factory

        if timeout is not None:
            async with async_timeout.timeout(timeout):
                results = await schedule_tasks()
        else:
            results = await schedule_tasks()

        return (
            results[0] if isinstance(results, list) and len(results) == 1 else results
        )
