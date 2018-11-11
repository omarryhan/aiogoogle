from ..utils import _dict



class Oauth2UserCreds(_dict):
    def __init__(self, *args, **kwargs):
        '''
        Viable parameters:
            access_token
            refresh_token
            expiry
        ''' 

class Oauth2ClientCreds(_dict):
    pass

class ApiKeyCreds(_dict):
    pass

class ServiceAccountKeyCreds(_dict):
    def __init__(self):
        pass