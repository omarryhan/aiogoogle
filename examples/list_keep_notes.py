#!/usr/bin/python3.7

'''
This won't work for your personal Google Keep profile.
Read more here: https://developers.google.com/keep/api
'''

import json
from pprint import pprint
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.resource import GoogleAPI
from aiogoogle.auth.creds import ServiceAccountCreds
import aiohttp


service_account_key = json.load(open('test_service_account.json'))

creds = ServiceAccountCreds(
    scopes=[
        "https://www.googleapis.com/auth/keep",
        "https://www.googleapis.com/auth/keep.readonly",
    ],
    **service_account_key
)

DISCOVERY_DOC_URL = 'https://keep.googleapis.com/$discovery/rest?version=v1'


async def list_notes():
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        async with aiohttp.ClientSession() as session:
            async with session.get(DISCOVERY_DOC_URL) as resp:
                disc_doc = await resp.json()
        keep = GoogleAPI(disc_doc)
        res = await aiogoogle.as_service_account(keep.notes.list())
        pprint(res)


if __name__ == "__main__":
    asyncio.run(list_notes())
