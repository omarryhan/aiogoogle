#!/usr/bin/python3.7

'''
Scopes Required:

* https://www.googleapis.com/auth/drive
* https://www.googleapis.com/auth/drive.file

API explorer link:

* https://developers.google.com/apis-explorer/#p/drive/v3/drive.files.create
'''

import asyncio
import sys
import mimetypes

from helpers import Aiogoogle, user_creds, client_creds


async def upload_file(full_path, new_name):
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        # Create API
        drive_v3 = await aiogoogle.discover("drive", "v3")

        req = drive_v3.files.create(
            upload_file=full_path,
            fields="id",
            json={"name": new_name}
        )

        # Usually autodetected by Drive
        # mimetypes autodetects the mimetype by file extension, which isn't always accurate. 
        # You may want to manually enter this for some extra assurance.
        req.upload_file_content_type = mimetypes.guess_type(full_path)[0] 

        # Upload file
        upload_res = await aiogoogle.as_user(req)
        print("Uploaded {} successfully.\nFile ID: {}".format(full_path, upload_res['id']))
        # file_id = upload_res["id"]
        # # Rename uploaded file
        # await aiogoogle.as_user(
        #     drive_v3.files.update(fileId=file_id, json={"name": new_name})
        # )
        # print("Renamed {} to {} successfully!".format(full_path, new_name))


if __name__ == "__main__":
    usage = "\n\nUsage:\n\nargv1: Full file path of the file you want to upload. e.g.: /home/omar/Desktop/note.txt\n\narg2: Upload name"
    try:
        full_path = sys.argv[1]
        new_name = sys.argv[2]
    except IndexError:
        print(usage)
        sys.exit(1)
    asyncio.run(upload_file(full_path, new_name))
