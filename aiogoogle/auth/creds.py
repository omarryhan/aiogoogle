from ..utils import _dict



class UserCreds(_dict):
    def __init__(self, *args, **kwargs):
        '''
        Viable parameters:
            access_token
            refresh_token
            expiry
        ''' 

class ClientCreds(_dict):
    pass

class ServiceAccountKeyCreds(_dict):
    def __init__(self):
        pass