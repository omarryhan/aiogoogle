#!/usr/bin/python3.7

import asyncio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email


async def create_signup_document():
    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as google:
        firestore = await google.discover("firestore", "v1")
        await google.as_user(
            firestore.projects.databases.documents.createDocument(
                parent="projects/{project_name}/databases/(default)/documents",
                collectionId="signups",
                json=dict(
                    fields={
                        "email": {"stringValue": email},
                        "addedAt": {
                            "timestampValue": datetime.datetime.utcnow().isoformat()
                            + "Z"
                        },
                        "anotherString": {"stringValue": anotherString},
                    }
                ),
                validate=False,  # "parent" validation has an invalid pattern. Our input is actually valid.
            ),
            user_creds=user_creds,
        )


if __name__ == "__main__":
    asyncio.run(create_signup_document())
