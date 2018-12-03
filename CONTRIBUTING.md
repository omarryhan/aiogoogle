# Contributing

Assuming you've read [this](https://www.contributor-covenant.org/version/1/4/code-of-conduct), here are some ideas:

## Features

- batch requests
- user_creds_jwt_auth
- supportsSubscription and channels
- additionalProperties (discovery)
- etag caching (aiohttp)
- Add asks (curio) session
- Create tasks with timeouts (aiohttp)
- Auth device code flow
- Service accounts
- Resumable upload (aiohttp):
  - https://cloud.google.com/storage/docs/json_api/v1/how-tos/resumable-upload
  - https://developers.google.com/drive/api/v3/resumable-upload
  - https://googlecloudplatform.github.io/google-resumable-media-python/0.1.0/google.resumable_media.requests.html
  - https://docs.aiohttp.org/en/stable/multipart.html
- validate repeated: Whether this parameter may appear multiple times. (add support for multidicts first)
- Write format checkers for `aiogoogle.validate.IGNORABLE_FORMATS`

## Optimization

- Chnage code with manual URL parsing to use a lightweight and reliable URL parsing lib

## Testing

- Search for `TODO:` in the `tests` module and you'll find lots of unimplemented tests
- test pattern vaildation.

## Docs

- Rewrite auth section and include openidconnect
- Add Spell checking

## Examples

## General

- Reonciliate aiogoogle.__version__.py.__verison__ && setup.py.version && docs.conf.py
