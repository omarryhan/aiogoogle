__all__ = []

from functools import wraps


def _toggle2x_dashed_params(f):
    @wraps(f)
    def wrapper(self, validate=None, data=None, json=None, upload_file=None, 
                download_file=None, timeout=None, **uri_params):
        '''
        Momentarily adds back '-' to url parameters and passed uri_params
        in order to be processed correctly and comply with the disc doc
        Reverts back to '_' after wrapped function is done
        '''
        # unfix urls
        uri_params = self._add_dash_user_uri_params(uri_params)
        
        # unfix params
        self._method_specs['parameters'] = self._add_dash_params(self._method_specs.get('parameters'))
        self._global_parameters = self._add_dash_params(self._global_parameters)

        # Run function
        results = f(self, validate, data, json, upload_file, download_file, timeout, **uri_params)

        # fix params again
        self._method_specs['parameters'] = self._rm_dash_params(self._method_specs.get('parameters'))
        self._global_parameters = self._rm_dash_params(self._global_parameters)

        return results
    return wrapper

def _safe_getitem(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError):
            return None
    return dct

class _dict(dict):  # pragma: no cover
    ''' A simple dict subclass. Nothing special '''
    def __init__(self, *args, **kwargs):  # pragma: no cover
        super(_dict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):  # pragma: no cover
        return self.get(attr)

    def __setattr__(self, key, value):  # pragma: no cover
        self.__setitem__(key, value)

    def __setitem__(self, key, value):  # pragma: no cover
        super(_dict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):  # pragma: no cover
        self.__delitem__(item)

    def __delitem__(self, key):  # pragma: no cover
        super(_dict, self).__delitem__(key)
        del self.__dict__[key]
