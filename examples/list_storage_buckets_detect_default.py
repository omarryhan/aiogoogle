#!/usr/bin/python3.7

from pprint import pprint
import os
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds


# Note
# ----
# When creating the service account. Don't forget to add an owner
# role in step 2 (after giving the service account a name).

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'test_service_account.json'

creds = ServiceAccountCreds(
    scopes=[
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/cloud-platform.read-only",
        "https://www.googleapis.com/auth/cloud-platform",
    ],
)


async def list_storage_buckets(project_id=creds["project_id"]):
    aiogoogle = Aiogoogle(service_account_creds=creds)
    await aiogoogle.service_account_manager.detect_default_creds_source()

    async with aiogoogle:
        storage = await aiogoogle.discover("storage", "v1")
        res = await aiogoogle.as_service_account(
            storage.buckets.list(project=creds["project_id"])
        )

    # Doing it again just to show that you only need to call
    # `detect_default_creds_source` once.
    async with aiogoogle:
        storage = await aiogoogle.discover("storage", "v1")
        res = await aiogoogle.as_service_account(
            storage.buckets.list(project=creds["project_id"])
        )

    pprint(res)


if __name__ == "__main__":
    asyncio.run(list_storage_buckets())
