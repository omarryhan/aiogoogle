import pprint
import json
import os

import pytest

from aiogoogle import DiscoveryClient
from aiogoogle.resource import Resource, Resources
from aiogoogle.models import Request, MediaDownload, MediaUpload, ResumableUpload
from aiogoogle.method import ResourceMethod
from aiogoogle.excs import ValidationError


from ...globals import SOME_APIS


def test_url_query_extra_not_included_and_warns(create_client):
    youtube = create_client('youtube', 'v3')
    with pytest.warns(UserWarning, match='i_am_extra'):
        req = youtube.resources.videos.list(part='snippet', i_am_extra=True, validate=False)
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?part=snippet'

def test_url_query_multi_query_arg(create_client):
    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.list(part='snippet', chart='idontknowhatthisisbutitshouldpass', validate=False)
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?part=snippet&chart=idontknowhatthisisbutitshouldpass'
    
def test_url_query_multi_query_arg_ordered_by_insertion(create_client):
    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.list(chart='idontknowhatthisisbutitshouldpass', part='snippet', validate=False)
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?chart=idontknowhatthisisbutitshouldpass&part=snippet'

def test_url_path_args_proper(create_client):
    calendar = create_client('calendar', 'v3')
    # Required path parameters are: 'calendarId' and 'ruleId'
    req = calendar.resources.acl.get(calendarId='uno', ruleId='dos', validate=False)
    assert req.url == 'https://www.googleapis.com/calendar/v3/calendars/uno/acl/dos'

def test_url_path_args_reversed(create_client):
    calendar = create_client('calendar', 'v3')
    # Should stay in the same order even if kwarg insertion was reversed
    req = calendar.resources.acl.get(ruleId='dos', calendarId='uno', validate=False)
    assert req.url == 'https://www.googleapis.com/calendar/v3/calendars/uno/acl/dos'

def test_url_path_args_reversed_with_extra_arg(create_client):
    calendar = create_client('calendar', 'v3')
    with pytest.warns(UserWarning, match='i_am_extra'):
        req = calendar.resources.acl.get(ruleId='dos', calendarId='uno', i_am_extra=1, validate=False)
    assert req.url == 'https://www.googleapis.com/calendar/v3/calendars/uno/acl/dos'

def test_url_path_args_and_query_path(create_client):
    calendar = create_client('calendar', 'v3')
    req = calendar.resources.events.get(eventId='dos', calendarId='uno', maxAttendees=1, validate=False)
    assert req.url == 'https://www.googleapis.com/calendar/v3/calendars/uno/events/dos?maxAttendees=1'

def test_url_path_args_and_query_path_extra_arg(create_client):
    calendar = create_client('calendar', 'v3')
    with pytest.warns(UserWarning, match='i_am_extra'):
        req = calendar.resources.events.get(i_am_extra=None, eventId='dos', calendarId='uno', maxAttendees=1, validate=False)
    assert req.url == 'https://www.googleapis.com/calendar/v3/calendars/uno/events/dos?maxAttendees=1'

def test_method(create_client):
    calendar = create_client('calendar', 'v3')
    req = calendar.resources.events.get(eventId='dos', calendarId='uno')
    assert req.method == 'GET'

def test_timeout(create_client):
    calendar = create_client('calendar', 'v3')
    req = calendar.resources.calendarList.get(calendarId=123, timeout=4, validate=False)
    assert req.timeout == 4

def test_timeout_fails_on_not_int(create_client):
    calendar = create_client('calendar', 'v3')
    with pytest.raises(TypeError) as e:
        calendar.resources.calendarList.get(calendarId=123, timeout=True, validate=False)
    assert 'int' in str(e)

    with pytest.raises(TypeError) as e:
        calendar.resources.calendarList.get(calendarId=123, timeout=False, validate=False)
    assert 'int' in str(e)

    with pytest.raises(TypeError) as e:
        calendar.resources.calendarList.get(calendarId=123, timeout='asas', validate=False)
    assert 'int' in str(e)

def test_json(create_client):
    JSON = {'etag': 'an_etag'}

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        json=JSON,
        validate=False
    )
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?autoLevels=True&part=snippet'
    assert req.json == JSON
    assert req.data is None

def test_data(create_client):
    DATA = {'etag': 'an_etag'}

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        data=DATA,
        validate=False
    )
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?autoLevels=True&part=snippet'
    assert req.data == DATA
    assert req.json is None

def test_data_str(create_client):
    DATA = 'asdasds'

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        data=DATA,
        validate=False
    )
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?autoLevels=True&part=snippet'
    assert req.data == DATA
    assert req.json is None

def test_data_and_json_fails(create_client):
    DATA = {'etag': 'an_etag'}
    JSON = {'etag2': 'an_etag'}

    youtube = create_client('youtube', 'v3')
    with pytest.raises(TypeError):
        youtube.resources.videos.insert(
            autoLevels=True,
            part='snippet',
            data=DATA,
            json=JSON,
            validate=False
        )

def test_download_file(create_client):
    DOWNLOAD_FILE = '/home/omar/Documents/captions.txt'

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.captions.download(id='a_path', download_file=DOWNLOAD_FILE, validate=True)
    assert req.media_download.file_path == DOWNLOAD_FILE

def test_download_file_unsupported_method_fails(create_client):
    DOWNLOAD_FILE = '/home/omar/Documents/captions.txt'

    youtube = create_client('youtube', 'v3')
    with pytest.raises(ValidationError) as e:
        youtube.resources.videos.list(part='irrelevant', download_file=DOWNLOAD_FILE, validate=True)
        assert 'download_file' in str(e)

def test_upload_file_name(create_client):
    UPLAOD_FILE_NAME = '/home/omar/Videos/video.mp4'

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        upload_file=UPLAOD_FILE_NAME,
        validate=False
    )
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?autoLevels=True&part=snippet'
    assert req.media_upload.file_path == UPLAOD_FILE_NAME

def test_upload_simple_path(create_client):
    UPLAOD_FILE_NAME = '/home/omar/Videos/video.mp4'

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        upload_file=UPLAOD_FILE_NAME,
        validate=False
    )
    assert req.media_upload.upload_path == 'https://www.googleapis.com/upload/youtube/v3/videos'

def test_upload_simple_multipart(create_client):
    UPLAOD_FILE_NAME = '/home/omar/Videos/video.mp4'

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        upload_file=UPLAOD_FILE_NAME,
        validate=False
    )
    assert req.media_upload.multipart is True

def test_upload_file_fails_unsupported_method(create_client):
    UPLAOD_FILE_NAME = '/home/omar/Videos/video.mp4'

    youtube = create_client('youtube', 'v3')
    with pytest.raises(ValidationError) as e:
        youtube.resources.videos.list(
            part='snippet',
            upload_file=UPLAOD_FILE_NAME,
            validate=True
        )
        assert 'upload_file' in str(e)

def test_resumable_upload(create_client):
    RESUMABLE_UPLOAD_SPECS = {
        'multipart': True,
        'path': '/resumable/upload/example/v3/resource'
    }
    METHOD_SPECS = {
        'path': 'resource/',
        'httpMethod': 'GET',
        'parameters': {},
        'supportsMediaUpload': True,
        'mediaUpload': {
            'accept': [
                "*/*",
                "application/octet-stream",
                "text/xml"
            ],

            'maxSize': "100MB",
            
            'protocols': {
                'simple': {
                    'multipart': True,
                    'path': "/upload/example/v3/resource"
                },
                'resumable': RESUMABLE_UPLOAD_SPECS
            },
        }
    }
    ROOT_URL = 'https://example.com/'
    BASE_URL = 'https://example.com/api/v1'

    method = ResourceMethod(name='upload', method_specs=METHOD_SPECS, global_parameters={}, schemas={}, base_url=BASE_URL, root_url=ROOT_URL, validate=False)
    req = method(upload_file='/home/omar/resumable_file.file')
    assert req.media_upload.resumable
    assert req.media_upload.resumable.upload_path == ROOT_URL[:-1] + RESUMABLE_UPLOAD_SPECS['path']
    assert req.media_upload.resumable.upload_path == 'https://example.com/resumable/upload/example/v3/resource'
    assert req.media_upload.resumable.multipart is True

def test_unresumable_upload(create_client):
    METHOD_SPECS = {
        'path': 'resource/',
        'httpMethod': 'GET',
        'parameters': {},
        'supportsMediaUpload': True,
        'mediaUpload': {
            'accept': [
                "*/*",
                "application/octet-stream",
                "text/xml"
            ],

            'maxSize': "100MB",
            
            'protocols': {
                'simple': {
                    'multipart': True,
                    'path': "/upload/example/v3/resource"
                }
            },
        }
    }
    ROOT_URL = 'https://example.com/'
    BASE_URL = 'https://example.com/api/v1'

    method = ResourceMethod(name='upload', method_specs=METHOD_SPECS, global_parameters={}, schemas={}, base_url=BASE_URL, root_url=ROOT_URL, validate=False)
    req = method(upload_file='/home/omar/resumable_file.file')
    assert req.media_upload.resumable is None
