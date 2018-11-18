import pprint
import json
import os

import pytest

from aiogoogle import DiscoveryClient
from aiogoogle.models import Resource, Resources, ResourceMethod, Request


from ..globals import SOME_APIS

@pytest.fixture('function')
def create_client():
    def wrapped(name, version):
        current_dir = os.getcwd()
        file_name = current_dir + '/tests/data/' + name + '_' + version + '_discovery_doc.json'
        with open(file_name, 'r') as discovery_doc:
            discovery_doc_dict = json.loads(discovery_doc.read())
        client = DiscoveryClient(discovery_document=discovery_doc_dict)
        return client
    return wrapped

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

def test_json(create_client):
    pass

def test_data(create_client):
    pass

def test_download_file(create_client):
    pass

def test_upload_file(create_client):
    UPLAOD_FILE_NAME = '/home/omar/Videos/video.mp4'
    JSON = {'etag': 'an_etag'}

    youtube = create_client('youtube', 'v3')
    req = youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        json=JSON,
        upload_file=UPLAOD_FILE_NAME,
        validate=False
    )
    assert req.url == 'https://www.googleapis.com/youtube/v3/videos?autoLevels=True&part=snippet'
    assert req.json == JSON
    assert req.media_upload.file_path == UPLAOD_FILE_NAME



    