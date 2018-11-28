# TODO: etag caching
# TODO: Multipart https://aiohttp.readthedocs.io/en/stable/multipart.html#aiohttp-multipart
# TODO: Create tasks with timeouts

__all__ = [
    'AiohttpSession'
]

import asyncio
from json import JSONDecodeError

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientResponseError, ContentTypeError
import aiofiles

from ..models import Response
from .abc import AbstractSession
from ..excs import HTTPError

class AiohttpSession(ClientSession, AbstractSession):
    def __init__(self, *args, **kwargs):
        if kwargs.get('timeout') is not None:
            kwargs['timeout'] = ClientTimeout(total=kwargs['timeout'])
        # Delete if None because aiohttp has a default timeout object set
        # to it's constructor's signature and it won't function without it
        elif 'timeout' in kwargs:
            del kwargs['timeout']
        super().__init__(*args, **kwargs)

    async def send(self, *requests, timeout=None, return_full_http_response=False, raise_for_status=True):
        def call_callback(request, response):
            if request.callback is not None:
                response.content = request.callback(response.content)
            return response

        async def resolve_response(request, response):
            data = None
            json = None
            download_file = None
            upload_file = None
            content = None


            # If downloading file:
            if request.media_download:
                download_file = request.media_download.file_path
                async with aiofiles.open(download_file, 'wb+') as download_file_fs:
                    while True:
                        chunk = await response.content.read()
                        if not chunk:
                            break
                        download_file_fs.write(chunk)
            else:
                if response.status != 204:  # If no (no content)
                    try:
                        content = await response.json()
                    except JSONDecodeError:
                        try:
                            content = await response.text(content_type=None)
                        except ContentTypeError:
                            content = await response.read(content_type=None)
                    if isinstance(response.content, dict):
                        json = content
                    else:
                        data = content
            
            if request.media_upload:
                upload_file = request.media_upload.file_path

            return Response(
                url = str(response.url),
                headers = response.headers,
                status_code = response.status,
                json = json,
                data = data,
                reason = response.reason if getattr(response, 'reason') else None,
                req = request,
                download_file = download_file,
                upload_file = upload_file
            )

        async def fire_request(request):
            request.headers['Accept-Encoding'] = 'gzip'
            if request.media_upload:
                async with aiofiles.open(request.media_upload.file_path, 'rb') as data:
                    return await self.request(
                        method = request.method,
                        url = request.url,
                        headers = request.headers,
                        data = data,
                        json = request.json,
                        timeout = request.timeout
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

        if return_full_http_response is True:
            tasks = [asyncio.create_task(get_response(request)) for request in requests]
        else:
            tasks = [asyncio.create_task(get_content(request)) for request in requests]

        results = await asyncio.gather(*tasks, return_exceptions=False)
        if isinstance(results, list) and len(results) == 1:
            return results[0]
        else:
            return results
