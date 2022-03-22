from datetime import datetime, timedelta
from typing import List

from nacl.exceptions import CryptoError
from nacl.public import SealedBox, PrivateKey, PublicKey
from nacl.utils import random as random_bytes

from .config.logger_config import logger

__secret_key: PrivateKey = PrivateKey(random_bytes())
__public_key: PublicKey = __secret_key.public_key
__enc_box: SealedBox = SealedBox(__public_key)
__dec_box: SealedBox = SealedBox(__secret_key)
del __secret_key
del __public_key


class Stamp:
    visitor_id: int
    place_id: int
    employee_id: int

    def __init__(self, employee_id: int, place_id: int, visitor_id: int):
        self.visitor_id: int = visitor_id
        self.place_id: int = place_id
        self.employee_id: int = employee_id


class InvalidStampToken(Exception):
    pass


def generate_stamp_token(employee_id: int, place_id: int) -> str:
    return __enc_box.encrypt(
        f"{employee_id}\n{place_id}\n{(datetime.utcnow() + timedelta(seconds=30)).isoformat()}"
        f"".encode('utf-8')
    ).hex()


def make_stamp(token: str, visitor_id: int) -> Stamp:
    try:
        # Decrypt the data from the token
        token: List[str] = __dec_box.decrypt(bytes.fromhex(token)) \
            .decode('utf-8').split('\n')

        logger.debug("Token decoded : {token}")
        logger.debug(f"time now :  {datetime.utcnow()}")
        logger.debug(f"token time: {datetime.fromisoformat(token[2])}")

        # Check if we have the 3 fields, if token hasn't expired, make a stamp
        if len(token) == 3 and datetime.utcnow() < datetime.fromisoformat(token[2]):
            logger.debug("Stamp is valid, return stamp...")
            return Stamp(*map(lambda x: int(x), token[:2]), visitor_id)
        else:
            logger.debug("Stamp invalid, raise exception")
            raise InvalidStampToken()
    except (ValueError, TypeError, CryptoError) as ex:
        logger.debug(ex)
        logger.debug("Decrypting error...")
        raise InvalidStampToken()
