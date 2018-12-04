__all__ = [
    'CurioAsksSession'
]

import curio
import asks
from asks import Session
asks.init('curio')

from .abc import AbstractSession
from ..models import Response


class CurioAsksSession(Session, AbstractSession):
    def __init__(self, *args, **kwargs):
        if kwargs.get('timeout'):
            del kwargs['timeout']
            kwargs.pop('timeout', None)
        super().__init__(*args, **kwargs)

    async def __aiter__(self):
        return self

    async def __aexit__(self, *args):
        pass

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
                raise NotImplementedError('Downloading media isn\'t supported by AsksSession')
            else:
                if response.status_code != 204:  # If no (no content)
                    try:
                        json = response.json()
                    except:
                        try:
                            data = response.text
                        except:
                            try:
                                data = response.content
                            except:
                                try:
                                    data = response.body
                                except:
                                    data = None
            
            if request.media_upload:
                upload_file = request.media_upload.file_path

            return Response(
                url=str(response.url),
                headers=response.headers,
                status_code=response.status_code,
                json=json,
                data=data,
                reason=response.reason_phrase if getattr(response, 'reason_phrase') else None,
                req=request,
                download_file=download_file,
                upload_file=upload_file,
                session_factory=session_factory
            )

        async def fire_request(request):
            request.headers['Accept-Encoding'] = 'gzip'
            if request.media_upload:
                raise NotImplementedError('Uploading media isn\'t supported by AsksSession')
            else:
                return await self.request(
                    method=request.method,
                    url=request.url,
                    headers=request.headers,
                    data=request.data,
                    json=request.json,
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

        async def execute_tasks():
            async with curio.TaskGroup() as g:
                if full_res is True:
                    tasks = [await g.spawn(get_response, request) for request in requests]
                else:
                    tasks = [await g.spawn(get_content, request) for request in requests]
            return await curio.gather(tasks)

        if session_factory is None:
            session_factory = self.__class__

        if timeout is not None:
            async with curio.timeout_after(timeout):
                results = await execute_tasks()
        else:
            results = await execute_tasks()
    
        if isinstance(results, list) and len(results) == 1:
            return results[0]
        else:
            return results
