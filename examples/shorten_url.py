#!/usr/bin/python3.7

import asyncio
import pprint

from helpers import Aiogoogle, api_key


async def shorten_urls(long_url):
    async with Aiogoogle(api_key=api_key) as google:
        url_shortener = await google.discover("urlshortener", "v1")
        short_url = await google.as_api_key(
            url_shortener.url.insert(json=dict(longUrl=long_url))
        )
    return short_url


if __name__ == "__main__":
    pprint.pprint(asyncio.run(shorten_urls("https://www.google.com")))
