import datetime

from aiogoogle.auth.utils import _get_expires_at


def test_get_expires_at():
    exp_str = _get_expires_at(120)
    exp_dt = datetime.datetime.fromisoformat(exp_str)
    assert exp_dt.tzinfo is None
    delta = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - exp_dt
    assert -1 < delta.seconds < 1
