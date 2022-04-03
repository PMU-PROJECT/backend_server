from datetime import datetime, timedelta
from typing import List

from nacl.exceptions import CryptoError
from nacl.public import SealedBox, PrivateKey, PublicKey
from nacl.utils import random as random_bytes
from sqlalchemy.ext.asyncio import AsyncSession

from .config.logger_config import logger
from .database.employees import Employees
from .id_token import get_id_from_token, InvalidIdToken

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


class InvalidStamp(Exception):
    pass


async def make_stamp(session: AsyncSession, token: str, employee_id: int) -> Stamp:
    """
    Make a stamp based on token scanned from user and employee_Did

    excepts:
        employee doesn't exist or 
    """
    employee = await Employees.by_id(session, employee_id)
    if employee is None:
        logger.debug("Employee doesn't exist!")
        raise InvalidStamp()

    place_id = employee.get("place_id")
    if place_id is None:
        logger.debug("Employee doesn't have an assigned place!")
        raise InvalidStamp()

    try:
        visitor_id = get_id_from_token(token)
        return Stamp(employee_id, place_id, visitor_id)
    except (ValueError, TypeError, CryptoError, InvalidIdToken) as ex:
        logger.debug(ex)
        raise InvalidStamp()
