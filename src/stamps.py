from datetime import datetime, timedelta
from typing import List

from nacl.exceptions import CryptoError
from nacl.public import SealedBox, PrivateKey, PublicKey
from nacl.utils import random as random_bytes

__secret_key: PrivateKey = PrivateKey(random_bytes())
__public_key: PublicKey = __secret_key.public_key
__enc_box: SealedBox = SealedBox(__public_key)
__dec_box: SealedBox = SealedBox(__secret_key)
del __secret_key
del __public_key


def generate_stamp_token(employee_id: int, place_id: int) -> str:
    return __enc_box.encrypt(
        f"{employee_id}\n{place_id}\n{(datetime.utcnow() + timedelta(seconds=30)).isoformat()}"
        f"".encode('utf-8')
    ).hex()


class Stamp:
    visitor_id: int
    place_id: int
    employee_id: int

    def __init__(self, employee_id: int, place_id: int, visitor_id: int):
        super(self).__init__()

        self.visitor_id: int = visitor_id
        self.place_id: int = place_id
        self.employee_id: int = employee_id


class InvalidToken(Exception):
    pass


def finish_stamping(token: str, visitor_id: int) -> Stamp:
    try:
        token: List[str] = __dec_box.decrypt(bytes.fromhex(token)) \
            .decode('utf-8').split('\n')

        if len(token) == 3:
            if datetime.utcnow() < datetime.fromisoformat(token[2]):
                return Stamp(*map(int, token[:2]), visitor_id)
    except (ValueError, TypeError, CryptoError):
        raise InvalidToken()
