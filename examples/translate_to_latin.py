#!/usr/bin/python3.7

import asyncio, pprint

from helpers import Aiogoogle, user_creds, client_creds, api_key, email


async def translate_to_latin(words):
    async with Aiogoogle(
        user_creds=user_creds, client_creds=client_creds, api_key=api_key
    ) as aiogoogle:
        language = await aiogoogle.discover("translate", "v2")
        words = dict(q=[words], target="la")
        result = await aiogoogle.as_api_key(language.translations.translate(json=words))
    pprint.pprint(result)


if __name__ == "__main__":
    asyncio.run(translate_to_latin("Aiogoogle is awesome"))
