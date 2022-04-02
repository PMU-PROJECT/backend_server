from datetime import datetime, timedelta
from typing import List

from nacl.exceptions import CryptoError
from nacl.public import SealedBox, PrivateKey, PublicKey
from nacl.utils import random as random_bytes
from sqlalchemy.ext.asyncio import AsyncSession

from .config.logger_config import logger
from .database.employees import Employees

__secret_key: PrivateKey = PrivateKey(random_bytes())
__public_key: PublicKey = __secret_key.public_key
__enc_box: SealedBox = SealedBox(__public_key)
__dec_box: SealedBox = SealedBox(__secret_key)
del __secret_key
del __public_key


class InvalidIdToken(Exception):
    pass


def generate_id_token(user_id: int) -> str:
    return __enc_box.encrypt(
        f"{user_id}\n{(datetime.utcnow() + timedelta(seconds=30)).isoformat()}"
        f"".encode('utf-8')
    ).hex()


def get_id_from_token(token: str) -> int:
    try:
        token: List[str] = __dec_box.decrypt(bytes.fromhex(token)) \
            .decode('utf-8').split('\n')
        if len(token) == 2:
            logger.debug("Token decoded : {token}")
            logger.debug(f"time now :  {datetime.utcnow()}")
            logger.debug(f"token time: {datetime.fromisoformat(token[1])}")

            # Check if we have the 2 fields, if token hasn't expired, make a stamp
            if datetime.utcnow() < datetime.fromisoformat(token[1]):
                logger.debug("token is valid, return id...")
                return int(token[0])
            else:
                logger.debug("token expired, raise exception")
                raise InvalidIdToken()

    except (ValueError, TypeError, CryptoError) as ex:
        logger.debug(ex)
        logger.debug("Decrypting error...")
        raise InvalidIdToken()
