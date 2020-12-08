from aiogoogle.auth.managers import ServiceAccountManager


def test_service_account_manager_instantiates_with_no_arguments():
    ServiceAccountManager()


def test_authorize():
    class Request:
        def __init__(self):
            pass

    man = ServiceAccountManager()
    man._access_token = '123'
    req = Request()
    req.headers = None

    authorized_req = man.authorize(req)

    assert authorized_req.headers['Authorization'] == 'Bearer 123'
