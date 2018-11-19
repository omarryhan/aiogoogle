import asyncio

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError
import aiofiles

from .abc import AbstractSession
from ..excs import HTTPError

class AiohttpSession(ClientSession, AbstractSession):

    async def send(self, *requests, timeout=None, return_full_http_response=False):
        # TODO: etag caching

        async def resolve_response(request, response):
            # If downloading file
            if request.media_download: 
                async with aiofiles.open(request.media_download.file_path, 'wb+') as download_file:
                    while True:
                        chunk = await response.content.read()
                        if not chunk:
                            break
                        download_file.write(chunk)
            else:
                if response.status == 204:  # If no content
                    response.content = None
                else:
                    response.content = await response.json(content_type=None)  # Any content type
            
            response.status_code = response.status
            return response

        def raise_for_status(response):
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise HTTPError(e)

        async def fire_request(request):
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
            return await resolve_response(request, response)
        async def get_content(request):
            response = await fire_request(request)
            raise_for_status(response)
            response = await resolve_response(request, response)
            return response.content
        #----------------- /coro runners ------------------#

        # 1. Create tasks
        # TODO: pass timeout when creating tasks
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
