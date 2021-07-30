#!/usr/bin/python3.7

import json
from pprint import pprint
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

'''
https://developers.google.com/apis-explorer/#search/storage/storage/v1/storage.buckets.list
'''

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


async def upload_storage_bucket(
    bucket="test_bucket_clientlib",
    file_name="one.csv",
    file_path="/mnt/c/Users/Omar/Desktop/one.csv",
    content_type="text/csv"
):
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        storage = await aiogoogle.discover("storage", "v1")
        req = storage.objects.insert(
            bucket=bucket,
            name=file_name,
            upload_file=file_path,
        )
        # You can autodetect mimetypes using python's built in `mimetypes` library
        req.upload_file_content_type = content_type
        res = await aiogoogle.as_service_account(req)
        pprint(res)

if __name__ == "__main__":
    asyncio.run(upload_storage_bucket())
