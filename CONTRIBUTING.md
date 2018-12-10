# Contributing

Assuming you've read [this](https://www.contributor-covenant.org/version/1/4/code-of-conduct), here are some ideas:

## Sort

make method generator global for test suite
treat empty "nextPageToken" the same as not found
contributing.md
Deal with youtube error

## Features

### Discovery

- batch requests
- supportsSubscription and channels
- Write format checkers for `aiogoogle.validate.IGNORABLE_FORMATS`

### Auth

- user_creds_jwt_auth
- Auth device code flow
- Service accounts/ iam

### Session

- etag caching (aiohttp)
- Resumable upload (aiohttp):
  - https://cloud.google.com/storage/docs/json_api/v1/how-tos/resumable-upload
  - https://developers.google.com/drive/api/v3/resumable-upload
  - https://googlecloudplatform.github.io/google-resumable-media-python/0.1.0/google.resumable_media.requests.html
  - https://docs.aiohttp.org/en/stable/multipart.html
- Handle fileio with Asks-Curio


## Optimization

- Chnage code with manual URL parsing to use a stdlib url parsing

## Testing

- Test gzip
- Currently, the library is extremely under tested. Writing some tests would be really appreciated.
- Search for `TODO:` in the `tests` module and you'll find lots of unimplemented tests

## Docs

- Spell check

## Examples

## General

- Reonciliate `aiogoogle.__version__.py.__verison__` && `setup.py.version` && `docs.conf.py`
