from typing import Type
from enum import Enum

from redbot.core.arke.backends.base import ArkeBackend
from redbot.core.arke.backends.sqlite import SQLiteBackend
from redbot.core.arke.backends.postgresql import PostgreSQLBackend
from redbot.core.arke.backends.mysql import MySQLBackend


class BackendType(Enum):
    SQLITE = 0
    POSTGRES = 1
    MYSQL = 2
    # Backends supported by Tortoise in its source code, but not documented
    # Keeping them here in case they're used one day
    MICROSOFTSQL = 3
    ODBC = 4  # Open Database Connectivity
    ORACLE = 5


def get_backend(type: BackendType) -> Type[ArkeBackend]:
    try:
        return {
            0: SQLiteBackend,
            1: PostgreSQLBackend,
            2: MySQLBackend
        }[type.value]
    except KeyError:
        raise ValueError(f"Backend {type.name} is not supported yet.")
