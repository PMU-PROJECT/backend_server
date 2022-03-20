from datetime import datetime, timedelta
from typing import List

from nacl.exceptions import CryptoError, InvalidkeyError
from nacl.public import SealedBox, PrivateKey, PublicKey
from nacl.pwhash.argon2id import str as argon2id, verify as verify_argon2id
from nacl.utils import random as random_bytes

__secret_key: PrivateKey = PrivateKey(random_bytes())
__public_key: PublicKey = __secret_key.public_key
__enc_box: SealedBox = SealedBox(__public_key)
__dec_box: SealedBox = SealedBox(__secret_key)
del __secret_key
del __public_key


class AuthenticationError(Exception):
    pass


def hash_password(password: str) -> bytes:
    return argon2id(password.encode('utf-8'))


def verify_password(password: str, password_hash: bytes) -> bool:
    try:
        return verify_argon2id(password_hash, password.encode('utf-8'))
    except (TypeError, InvalidkeyError):
        return False


def generate_token(data) -> str:
    return __enc_box.encrypt(
        f"{data}\n{(datetime.utcnow() + timedelta(hours=3)).isoformat()}"
        f"".encode('utf-8')
    ).hex()


def validate_token(token: str) -> str:
    try:
        token: List[str] = __dec_box.decrypt(bytes.fromhex(token)) \
            .decode('utf-8').split('\n')

        if len(token) == 2:
            if datetime.utcnow() < datetime.fromisoformat(token[1]):
                return token[0]
    except (ValueError, TypeError, CryptoError):
        raise AuthenticationError()
