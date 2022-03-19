from typing import Any, Iterable, MutableMapping

from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.schema import Column, Constraint, ForeignKey
from sqlalchemy.types import BigInteger


@as_declarative()
class ORMBase(object):
    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


def id_column(
        name: str,
        constraints: Iterable[Constraint] = [],
        options: MutableMapping[str, Any] = {},
):
    options.update(
        autoincrement=True,
        onupdate='restrict',
        primary_key=True,
        nullable=False,
    )

    return Column(
        name,
        BigInteger(),
        *constraints,
        **options,
    )


def id_ref_column(
        name: str,
        column: Column,
        constraints: Iterable[Constraint] = [],
        options: MutableMapping[str, Any] = {},
):
    options.update(
        autoincrement=None,
    )
    return Column(
        name,
        BigInteger(),
        ForeignKey(
            column,
            onupdate='restrict',
            ondelete='restrict',
        ),
        *constraints,
        **options,
    )
