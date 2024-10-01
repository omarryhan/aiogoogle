import datetime

from aiogoogle.auth.utils import _get_expires_at, _is_expired


def test_get_expires_at():
    exp_str = _get_expires_at(120)
    exp_dt = datetime.datetime.fromisoformat(exp_str)
    assert exp_dt.tzinfo is None
    delta = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - exp_dt
    assert -1 < delta.seconds < 1


def test_is_expired():
    # correctness not tested, but none of these should raise an exception
    _is_expired("2024-10-01T14:26:21")
    _is_expired("2024-10-01T14:26:21Z")
    _is_expired(datetime.datetime.now())
    _is_expired(datetime.datetime.now(datetime.timezone.utc))
