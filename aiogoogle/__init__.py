__all__ = [
    'DiscoveryClient'
]

from . import _jsonschema
_jsonschema.patch()

from .client import DiscoveryClient