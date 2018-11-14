import asyncio

from aiohttp import ClientSession
import aiofiles

from .abc import AbstractSession
from ..excs import HTTPError

class AiohttpSession(ClientSession, AbstractSession):

    async def send(self, *requests, return_full_response=False, return_tasks=False):
        async def resolve_response(request, response):
            # If downloading file
            if request.chunked_download is True:
                async with aiofiles.open(request.download_file_name, 'wb') as download_file:
                    while True:
                        chunk = await response.content.read()
                        if not chunk:
                            break
                        download_file.write(chunk)
            else:
                if response.status == 204:  # If no content
                    response.content = None
                else:
                    response.content = await response.json(content_type=None)  # Not necessarily JSON. This assures it isn't in bytes
            
            response.status_code = response.status
            return response

        def raise_for_status(response):
            try:
                response.raise_for_status()
            except Exception as e:
                raise HTTPError(e)

        async def fire_request(request):
            # If uploading file
            if request.chunked_upload is True:
                async with aiofiles.open(request.upload_file_name) as data:
                    return await self.request(
                        method = request.method,
                        url = request.url,
                        headers = request.headers,
                        data = data,
                        json = request.json
                    )
            else:
                return await self.request(
                    method = request.method,
                    url = request.url,
                    headers = request.headers,
                    data = request.data,
                    json = request.json
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
        if return_full_response is True:
            tasks = [asyncio.create_task(get_response(request)) for request in requests]
        else:
            tasks = [asyncio.create_task(get_content(request)) for request in requests]

        # 2. Return if tasks were needed
        if return_tasks:
            if isinstance(tasks, list) and len(tasks) == 1:
                return tasks[0]
            else:
                return tasks

        # 3. Else await tasks and return results
        else:
            results = await asyncio.gather(*tasks, return_exceptions=False)
            if isinstance(results, list) and len(results) == 1:
                return results[0]
            else:
                return results
        