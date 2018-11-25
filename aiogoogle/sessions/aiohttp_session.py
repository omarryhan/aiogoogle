# TODO: etag caching
# TODO: Multipart https://aiohttp.readthedocs.io/en/stable/multipart.html#aiohttp-multipart
# TODO: Create tasks with timeouts

__all__ = [
    'AiohttpSession'
]

import asyncio

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientResponseError
import aiofiles

from ..models import Response
from .abc import AbstractSession
from ..excs import HTTPError

class AiohttpSession(ClientSession, AbstractSession):
    def __init__(self, *args, **kwargs):
        if kwargs.get('timeout') is not None:
            kwargs['timeout'] = ClientTimeout(total=kwargs['timeout'])
        else:
            kwargs.pop('timeout')
        super().__init__(*args, **kwargs)

    async def send(self, *requests, timeout=None, return_full_http_response=False):
        def call_callback(request, response):
            if request.callback is not None:
                response.content = request.callback(response.content)
            return response

        async def resolve_response(request, response):

            data = None
            json = None
            download_file = None
            upload_file = None


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
                    response.content = await response.json(content_type=None)  # Any content type
                    if isinstance(response.content, dict):
                        json = response.content
                    else:
                        data = response.content
            
            if request.media_upload:
                upload_file = request.media_upload.file_path

            return Response(
                url = str(response.url),
                headers = response.headers,
                status_code = response.status,
                json = json,
                data = data,
                download_file = download_file,
                upload_file = upload_file
            )

        def raise_for_status(response):
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise HTTPError(e)

        async def fire_request(request):
            # Add accept gzip header
            request.headers['Accept-Encoding'] = 'gzip'
            # If uploading file
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

        #----------------- coro runners ------------------#
        async def get_response(request):
            response = await fire_request(request)
            raise_for_status(response)
            response = await resolve_response(request, response)
            response = call_callback(request, response)
            return response
        async def get_content(request):
            response = await fire_request(request)
            raise_for_status(response)
            response = await resolve_response(request, response)
            response = call_callback(request, response)
            return response.content
        #----------------- /coro runners ------------------#

        # 1. Create tasks
        if return_full_http_response is True:
            tasks = [asyncio.create_task(get_response(request)) for request in requests]
        else:
            tasks = [asyncio.create_task(get_content(request)) for request in requests]

        # 2. await tasks and return results
        results = await asyncio.gather(*tasks, return_exceptions=False)
        if isinstance(results, list) and len(results) == 1:
            return results[0]
        else:
            return results
