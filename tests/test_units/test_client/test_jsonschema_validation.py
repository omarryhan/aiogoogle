import pprint
import json
import os

import pytest

from aiogoogle import DiscoveryClient
from aiogoogle.resource import Resource, Resources
from aiogoogle.method import ResourceMethod
from aiogoogle.models import Request
from aiogoogle.excs import ValidationError


from ...globals import SOME_APIS


def test_validates_url_path_params(create_client):
    calendar = create_client('calendar', 'v3')
    assert calendar.resources.acl.insert(calendarId='string', validate=True)

    with pytest.raises(ValidationError):
        calendar.resources.acl.insert(calendarId=1, validate=True)
        calendar.resources.acl.insert(calendarId=None, validate=True)
        calendar.resources.acl.insert(calendarId=True, validate=True)
        calendar.resources.acl.insert(calendarId=['asdasd'], validate=True)


def test_validates_url_query_params(create_client):
    youtube = create_client('youtube', 'v3')
    youtube.resources.videos.list(part='snippet', validate=True)

    with pytest.raises(ValidationError):
        youtube.resources.videos.list(part=0.8, validate=True)
        youtube.resources.videos.list(part=False, validate=True)
        youtube.resources.videos.list(part=1, validate=True)
        youtube.resources.videos.list(part=('snippet'), validate=True)

def test_validates_body_data(create_client):
    # Also tests ref resolution as the Video schmea has nested $refs that need to be resolved
    youtube = create_client('youtube', 'v3')
    youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        data=dict(ageGating=dict(alcoholContent=True)),
        validate=True
    )

    with pytest.raises(ValidationError):
        youtube.resources.videos.insert(
            autoLevels=True,
            part='snippet',
            data=1.82,
            validate=True
        )

def test_validates_body_json(create_client):
    # Also tests ref resolution as the Video schmea has nested $refs that need to be resolved
    youtube = create_client('youtube', 'v3')
    youtube.resources.videos.insert(
        autoLevels=True,
        part='snippet',
        json=dict(ageGating=dict(alcoholContent=True)),
        validate=True
    )

    with pytest.raises(ValidationError):
        youtube.resources.videos.insert(
            autoLevels=True,
            part='snippet',
            json=False,
            validate=True
        )