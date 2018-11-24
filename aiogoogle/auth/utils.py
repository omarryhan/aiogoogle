__all__ = []
import secrets


def _create_secret(bytes_length=32):  # pragma: no cover
    return secrets.base64.standard_b64encode(secrets.token_bytes(bytes_length)).decode('utf-8')