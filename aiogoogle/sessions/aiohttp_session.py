__all__ = [
    'AiohttpSession'
]

import asyncio
from json import JSONDecodeError

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientResponseError, ContentTypeError
import aiofiles
from aiofiles import os as async_os

from ..models import Response
from .abc import AbstractSession
from ..excs import HTTPError, ValidationError



class AiohttpSession(ClientSession, AbstractSession):
    def __init__(self, *args, **kwargs):
        if kwargs.get('timeout') is not None:
            kwargs['timeout'] = ClientTimeout(total=kwargs['timeout'])
        # Delete if None because aiohttp has a default timeout object set
        # to it's constructor's signature and it won't function without it
        elif 'timeout' in kwargs:
            del kwargs['timeout']
        super().__init__(*args, **kwargs)

    async def send(self, *requests, timeout=None, full_res=False, raise_for_status=True, session_factory=None):
        def call_callback(request, response):
            if request.callback is not None:
                if response.json:
                    response.json = request.callback(response.content)
                elif response.data:
                    response.data = request.callback(response.content)
            return response

        async def resolve_response(request, response):
            data = None
            json = None
            download_file = None
            upload_file = None

            # If downloading file:
            if request.media_download:
                download_file = request.media_download.file_path
                async with aiofiles.open(download_file, 'wb+') as f:
                    async for line in response.content:
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
                reason=response.reason if getattr(response, 'reason') else None,
                req=request,
                download_file=download_file,
                upload_file=upload_file,
                session_factory=session_factory
            )

        async def aiter_file(file_name, chunk_size):
            ''' Async file generator '''
            async with aiofiles.open(file_name, 'rb') as f:
                chunk = await f.read(chunk_size)
                while chunk:
                    yield chunk
                    chunk = await f.read(chunk_size)

        async def get_file_size(full_file_path):
            stat = await async_os.stat(full_file_path)
            return stat.st_size

        async def fire_request(request):
            request.headers['Accept-Encoding'] = 'gzip'
            if request.media_upload:
                # Validate
                if request.media_upload.validate is True and request.media_upload.max_size is not None:
                    size = await get_file_size(request.media_upload.file_path)
                    max_size = request.media_upload.max_size
                    if size > max_size:
                        raise ValidationError(
                            f'"{request.media_upload.file_path}" has a size of {size/1000}KB. Max upload size for this endpoint is: {max_size/1000}KB.'
                        )

                # If multipart pass a file async generator 
                if request.media_upload.multipart is True:
                    return await self.request(
                        method=request.method,
                        url=request.media_upload.upload_path,
                        headers=request.headers,
                        data=aiter_file(request.media_upload.file_path, request.media_upload.chunk_size),
                        json=request.json,
                        timeout=request.timeout
                    )
                # Else load file to memory and send
                else:
                    async with aiofiles.open(request.media_upload.file_path, 'rb') as file:
                        read_file = await file.read()
                        return await self.request(
                            method=request.method,
                            url=request.media_upload.upload_path,
                            headers=request.headers,
                            data=read_file,
                            json=request.json,
                            timeout=request.timeout
                    )
            else:
                return await self.request(
                    method = request.method,
                    url = request.url,
                    headers = request.headers,
                    data = request.data,
                    json = request.json,
                    timeout = request.timeout
                )

        #----------------- runners ------------------#
        async def get_response(request):
            response = await fire_request(request)
            response = await resolve_response(request, response)
            if raise_for_status is True:
                response.raise_for_status()
            response = call_callback(request, response)
            return response
        async def get_content(request):
            response = await get_response(request)
            return response.content
        #----------------- /runners ------------------#

        if session_factory is None:
            session_factory = self.__class__

        if full_res is True:
            tasks = [asyncio.create_task(get_response(request)) for request in requests]
        else:
            tasks = [asyncio.create_task(get_content(request)) for request in requests]

        results = await asyncio.gather(*tasks, return_exceptions=False)
        if isinstance(results, list) and len(results) == 1:
            return results[0]
        else:
            return results
