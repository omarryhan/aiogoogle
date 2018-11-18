import pytest

import pprint
from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod, Request, MediaDownload, MediaUpload, ResumableUpload
from ..globals import SOME_APIS

def test_request_constructor():
    req = Request(
        method='GET',
        url='https://example.com/api/v1/example_resource?example_query=example_arg',
        headers={'Authorization': 'Bearer asdasdasd'},
        json={'data': 'asasdasd'},
        media_upload=MediaUpload('asdasd'),
        media_download=MediaDownload('assda')
    )

# TODO
# def test_batch_request():
#     pass

