from aiohttp import ClientSession

from .abc import AbstractSession

class AiohttpSession(ClientSession):

    __metaclass__ =  AbstractSession

    async def send(self, *requests, return_json_only=True, raise_for_status=True, return_tasks=False):
        pass