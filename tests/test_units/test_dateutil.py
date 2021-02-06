import pytest

from datetime import datetime
from aiogoogle.utils import _parse_isoformat


def test_iso_parser1():
    assert _parse_isoformat("2021-02-06") == datetime(2021, 2, 6)

def test_iso_parser2():
    assert _parse_isoformat("2021-02-06T14") == datetime(2021, 2, 6, 14)

def test_iso_parser3():
    assert _parse_isoformat("2021-02-06T14:52") == datetime(2021, 2, 6, 14, 52)

def test_iso_parser4():
    assert _parse_isoformat("2021-02-06T14:52:26") == \
        datetime(2021, 2, 6, 14, 52, 26)

def test_iso_parser5():
    assert _parse_isoformat("2021-02-06T14:52:26.123") == \
        datetime(2021, 2, 6, 14, 52, 26, 123000)

def test_iso_parser6():
    assert _parse_isoformat("2021-02-06T14:52:26.123456") == \
        datetime(2021, 2, 6, 14, 52, 26, 123456)

def test_iso_parser7():
    assert _parse_isoformat("2021-02-06T14:52:26.123456+01:30") == \
        datetime(2021, 2, 6, 13, 22, 26, 123456)

def test_iso_parser8():
    assert _parse_isoformat("2021-02-06T14:52:26.123456-01:00") == \
        datetime(2021, 2, 6, 15, 52, 26, 123456)

def test_iso_malformed1():
    with pytest.raises(ValueError):
        _parse_isoformat("2021-02T14:52")

def test_iso_malformed2():
    with pytest.raises(ValueError):
        _parse_isoformat("2021-02-06T")

def test_iso_malformed3():
    with pytest.raises(ValueError):
        _parse_isoformat("2021-02-06T14.123")

def test_iso_malformed4():
    with pytest.raises(ValueError):
        _parse_isoformat("2021-02-06T14:52.123456")

def test_iso_malformed5():
    with pytest.raises(ValueError):
        _parse_isoformat("2021-02-06T14:52:26.1234")
