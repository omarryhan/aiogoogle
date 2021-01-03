#!/usr/bin/python3.7

"""Upload files to Google Cloud Storage using asynchronous calls"""

from typing import List, Dict, Tuple
import asyncio

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds

creds = ServiceAccountCreds(
    scopes=[
        "https://www.googleapis.com/auth/devstorage.read_only",
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/devstorage.full_control",
        "https://www.googleapis.com/auth/cloud-platform.read-only",
        "https://www.googleapis.com/auth/cloud-platform",
    ],
)

aiogoogle_factory = Aiogoogle(service_account_creds=creds)


async def get_creds():
    """Set up the credentials for aiogoogle"""
    await aiogoogle_factory.service_account_manager.detect_default_creds_source()


asyncio.run(get_creds())


async def async_gcs(file_list: List[Tuple[str, str, str]], bucket: str):
    async with aiogoogle_factory:
        storage = await aiogoogle_factory.discover("storage", "v1")
        requests = []
        for file_name, file_path, mime_type in file_list:
            req = storage.objects.insert(bucket=bucket, name=file_name, upload_file=file_path)
            # add the mime_type to the headers. You can autodetect mimetypes using python's
            # built in `mimetypes` library
            req.headers = {'Content-Type': mime_type}
            requests.append(req)
        results = await aiogoogle_factory.as_service_account(*requests, full_res=True)
    return [results.json] if len(file_list) == 1 else [result.json for result in results]


def upload_files_parallel(file_list: List[Tuple[str, str, str]], bucket: str) -> List[Dict]:
    return asyncio.run(async_gcs(file_list, bucket))


if __name__ == "__main__":
    file_path_1, file_path_2 = "file_1.txt", "file_2.txt"
    file_mime_type_1, file_mime_type_2 = "text/plain", "text/plain"
    file_target_blob_name_1, file_target_blob_name_2 = "files/file_1.txt", "files/file_2.txt"
    with open(file_path_1, 'w') as file_1:
        file_1.writelines(["Hello", "World"])
    with open(file_path_2, 'w') as file_2:
        file_2.writelines(["Well", "hello", "there"])
    file_list = [
        (file_target_blob_name_1, file_path_1, file_mime_type_1),
        (file_target_blob_name_2, file_path_2, file_mime_type_2),
    ]
    bucket = "my-bucket"
    upload_results = upload_files_parallel(file_list, bucket)
