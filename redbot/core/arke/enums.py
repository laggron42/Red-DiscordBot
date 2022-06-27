from enum import Enum


class Backend(Enum):
    sqlite = "tortoise.backends.sqlite"
    postgres = "tortoise.backends.asyncpg"
    mysql = "toirtoise.backends.mysql"
