__all__ = ["create_secret"]
import hashlib
import os


def create_secret(bytes_length=1024):  # pragma: no cover
    # return hashlib.sha256(os.urandom(bytes_length << 3)).hexdigest()
    return hashlib.sha256(os.urandom(bytes_length)).hexdigest()
