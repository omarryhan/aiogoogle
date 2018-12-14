import json
import os

import pytest

from aiogoogle.resource import Resource, GoogleAPI, Method
from aiogoogle.models import Request
from aiogoogle.excs import ValidationError


from ..test_globals import ALL_APIS


# TODO: Test additionalParameters (Tricky as it's not in compliance with jsonschema3)

def test_aiogoogle_compiles_discovery_re_pattern(create_api):
    pass

def test_validates_url_path_params(create_api):
    calendar = create_api('calendar', 'v3')
    assert calendar.acl.insert(calendarId='string', validate=True)

    with pytest.raises(ValidationError):
        calendar.acl.insert(calendarId=1, validate=True)
    with pytest.raises(ValidationError):
        calendar.acl.insert(calendarId=None, validate=True)
    with pytest.raises(ValidationError):
        calendar.acl.insert(calendarId=True, validate=True)
    with pytest.raises(ValidationError):
        calendar.acl.insert(calendarId=['asdasd'], validate=True)


def test_validates_url_query_params(create_api):
    youtube = create_api('youtube', 'v3')
    youtube.videos.list(part='snippet', validate=True)

    with pytest.raises(ValidationError):
        youtube.videos.list(part=0.8, validate=True)
    with pytest.raises(ValidationError):
        youtube.videos.list(part=False, validate=True)
    with pytest.raises(ValidationError):
        youtube.videos.list(part=1, validate=True)
    with pytest.raises(ValidationError):
        youtube.videos.list(part=['snippet'], validate=True)

def test_validates_body_data(create_api):
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
    youtube = create_api('youtube', 'v3')
    youtube.videos.insert(
        autoLevels=True,
        part='snippet',
        json=dict(ageGating=dict(alcoholContent=True)),
        validate=True
    )

def test_validates_body_json_2(create_api):
    youtube = create_api('youtube', 'v3')
    with pytest.raises(ValidationError):
        youtube.videos.insert(
            autoLevels=True,
            part='snippet',
            json=False,
            validate=True
        )

def test_validates_body_json_3(create_api):
    youtube = create_api('youtube', 'v3')
    with pytest.raises(ValidationError):
        youtube.videos.insert(
            autoLevels=True,
            part='snippet',
            json=dict(ageGating=dict(alcoholContent='asdasdasdasd')),
            validate=True
        )

def test_validates_body_json_4(create_api):
    youtube = create_api('youtube', 'v3')
    with pytest.raises(ValidationError):
        youtube.videos.insert(
            autoLevels=True,
            part='snippet',
            json=dict(ageGating=dict(alcoholContent={'asdasdkj': 'asdads'})),
            validate=True
        )

def test_validates_body_json_5(create_api):
    youtube = create_api('youtube', 'v3')
    youtube.videos.insert(
        autoLevels=True,
        part='snippet',
        json=None,
        validate=True
    )

def test_validates_body_json_6(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.get(
        calendarId='asdasd',
        validate=True
    )

def test_validates_body_json_7(create_api):
    calendar = create_api('calendar', 'v3')
    with pytest.raises(ValidationError):
        calendar.calendarList.get(
            calendarId=True,
            validate=True
        )

def test_validates_body_json_8(create_api):
    calendar = create_api('calendar', 'v3')
    with pytest.raises(ValidationError):
        calendar.calendarList.get(
            calendarId=123,
            validate=True
        )

def test_validates_body_json_9(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json='asdasd',
            validate=True
        )

def test_validates_body_json_10(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json=[],
            validate=True
        )
def test_validates_body_json_11(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    calendar.calendarList.list(
        json={},
        validate=True
    )

def test_validates_body_json_12(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json={
                'items':{}
            }
        )

def test_validates_body_json_13(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    calendar.calendarList.list(
        json={
            'items':[
                {
                    'accessRole': 'a_valid_access_role'
                },
            ]
        }
    )

def test_validates_body_json_14(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json={
                'items':[
                    {
                        'accessRole': 1
                    },
                ]
            }
        )

def test_validates_body_json_15(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        calendar.calendarList.list(
            json={
                'items':[
                    {
                        'accessRole': 'a_valid_access_role'
                    },
                    {
                        'this_isnt_supposed_to_be_here': True
                    }
                ]
            }
        )

def test_validates_body_json_16(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        calendar.calendarList.list(
            json={
                'items':[
                    {
                        'accessRole': 'a_valid_access_role'
                    },
                    {
                        'this_isnt_supposed_to_be_here': 'asdasdasd'
                    }
                ]
            }
        )

def test_validates_body_json_17(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        calendar.calendarList.list(
            json={
                'items':[
                    {
                        'this_isnt_supposed_to_be_here': True
                    }
                ]
            }
        )

def test_validates_body_json_18(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        calendar.calendarList.list(
            json={
                'items':[
                    {
                        'this_isnt_supposed_to_be_here': 'asdasdasd'
                    }
                ]
            }
        )

def test_validates_body_json_19(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        with pytest.raises(ValidationError):
            calendar.calendarList.list(
                json={
                    'items':[
                        {
                            'accessRole': 1,
                            'this_isnt_supposed_to_be_here': 123
                        },
                    ]
                }
            )

def test_validates_body_json_20(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.warns(UserWarning, match='this_isnt_supposed_to_be_here'):
        with pytest.raises(ValidationError):
            calendar.calendarList.list(
                json={
                    'items':[
                        {
                            'accessRole': 1,
                            'this_isnt_supposed_to_be_here': 'asdsda'
                        },
                    ]
                }
            )

def test_validates_body_json_21(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    calendar.calendarList.list(
        json={
            'etag': 'asd',
            'items':[
                {
                    'accessRole': 'asdasd',
                    'defaultReminders': [
                        {
                            'method': 'asd',
                            'minutes': 1
                        },
                        {
                            'method': 'asd',
                            'minutes': 1
                        },
                    ]
                },
            ]
        }
    )

def test_validates_body_json_22(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json={
                'etag': 'asd',
                'items':[
                    {
                        'accessRole': 'asdasd',
                        'defaultReminders': [
                            {
                                'method': 'asd',
                                'minutes': '123'
                            },
                            {
                                'method': 'asd',
                                'minutes': 1
                            },
                        ]
                    },
                ]
            }
        )

def test_validates_body_json_23(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json={
                'etag': 'asd',
                'items':[
                    {
                        'accessRole': 'asdasd',
                        'defaultReminders': [
                            {
                                'method': 'asd',
                                'minutes': 1
                            },
                            {
                                'method': 'asd',
                                'minutes': 1
                            },
                            'asd'
                        ]
                    },
                ]
            }
        )

def test_validates_body_json_24(create_api):
    calendar = create_api('calendar', 'v3')
    calendar.calendarList.list(validate=True)
    calendar.calendarList.list._method_specs['request'] = calendar.calendarList.list._method_specs['response']  # Testing arrays and objects
    with pytest.raises(ValidationError):
        calendar.calendarList.list(
            json={
                'etag': 'asd',
                'items':[
                    {
                        'accessRole': 3,
                        'defaultReminders': [
                            {
                                'method': 'asd',
                                'minutes': 1
                            },
                            {
                                'method': 'asd',
                                'minutes': 1
                            },
                        ]
                    },
                ]
            }
        )