#!/usr/bin/python3.7

import json
from pprint import pprint
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

'''
https://developers.google.com/apis-explorer/#search/storage/storage/v1/storage.buckets.list
'''

# Note
# ----
# When creating the service account. Don't forget to add an owner
# role in step 2 (after giving the service account a name).

service_account_key = json.load(open('test_service_account.json'))

creds = ServiceAccountCreds(
    scopes=[
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/cloud-platform.read-only",
        "https://www.googleapis.com/auth/cloud-platform",
    ],
    **service_account_key
)


async def list_storage_buckets(project_id=creds["project_id"]):
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        storage = await aiogoogle.discover("storage", "v1")
        res = await aiogoogle.as_service_account(
            storage.buckets.list(project=creds["project_id"])
        )
        pprint(res)


if __name__ == "__main__":
    asyncio.run(list_storage_buckets())
