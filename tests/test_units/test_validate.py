import pprint
import json
import os

import pytest

from aiogoogle.resource import Resource, GoogleAPI, Method
from aiogoogle.models import Request
from aiogoogle.excs import ValidationError


from ..globals import SOME_APIS


def test_validates_url_path_params(create_api):
    calendar = create_api('calendar', 'v3')
    assert calendar.acl.insert(calendarId='string', validate=True)

    with pytest.raises(ValidationError):
        calendar.acl.insert(calendarId=1, validate=True)
        calendar.acl.insert(calendarId=None, validate=True)
        calendar.acl.insert(calendarId=True, validate=True)
        calendar.acl.insert(calendarId=['asdasd'], validate=True)


def test_validates_url_query_params(create_api):
    youtube = create_api('youtube', 'v3')
    youtube.videos.list(part='snippet', validate=True)

    with pytest.raises(ValidationError):
        youtube.videos.list(part=0.8, validate=True)
        youtube.videos.list(part=False, validate=True)
        youtube.videos.list(part=1, validate=True)
        youtube.videos.list(part=('snippet'), validate=True)

def test_validates_body_data(create_api):
    # Also tests ref resolution as the Video schmea has nested $refs that need to be resolved
    youtube = create_api('youtube', 'v3')
    youtube.videos.insert(
        autoLevels=True,
        part='snippet',
        data=dict(ageGating=dict(alcoholContent=True)),
        validate=True
    )

    with pytest.raises(ValidationError):
        youtube.videos.insert(
            autoLevels=True,
            part='snippet',
            data=1.82,
            validate=True
        )

def test_validates_body_json(create_api):
    # Also tests ref resolution as the Video schmea has nested $refs that need to be resolved
    youtube = create_api('youtube', 'v3')
    youtube.videos.insert(
        autoLevels=True,
        part='snippet',
        json=dict(ageGating=dict(alcoholContent=True)),
        validate=True
    )

    with pytest.raises(ValidationError):
        youtube.videos.insert(
            autoLevels=True,
            part='snippet',
            json=False,
            validate=True
        )