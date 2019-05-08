__all__ = []


def _safe_getitem(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError):
            return None
    return dct


class _dict(dict):  # pragma: no cover
    """ A simple dict subclass for use with Creds modelling. No surprises """

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
