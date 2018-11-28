__all__ = ['create_secret']
import secrets
import hashlib
import os


def create_secret(bytes_length=32):  # pragma: no cover
    return hashlib.sha256(os.urandom(1024)).hexdigest()