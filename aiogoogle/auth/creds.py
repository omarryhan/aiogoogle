from ..utils import _dict


class APIKey(str):
    pass

class UserCreds(_dict):
    '''
    access_token
    created_at: datetime in json
    '''
    pass

class ClientCreds(_dict):
    pass

class ServiceAccountKeyCreds(_dict):
    pass