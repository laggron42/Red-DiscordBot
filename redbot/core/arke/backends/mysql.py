import sys
import getpass

from redbot.core.arke.backends.base import ArkeBackend

from typing import TypedDict


class Settings(TypedDict):
    user: str
    password: str
    host: int
    port: int
    db_prefix: str


class MySQLBackend(ArkeBackend[Settings]):
    @staticmethod
    def prompt_backend_settings() -> dict:
        host = (
            input(
                f"Enter the MySQL/MariaDB server's address.\n"
                f"> "
            )
            or None
        )

        print(
            "Enter the PostgreSQL server port.\n"
            "If left blank, this will default to 3306."
        )
        while True:
            port = input("> ") or None
            if port is None:
                break
            try:
                port = int(port)
            except ValueError:
                print("Port must be a number")
            else:
                break

        user = (
            input(
                "Enter the PostgreSQL server username.\n"
                "> "
            )
            or None
        )

        password = getpass.getpass(
            f"Enter the PostgreSQL server password. The input will be hidden.\n"
            f"> "
        )
        if password == "NONE":
            password = None

        return {"host": host, "port": port, "user": user, "password": password}

    @property
    def tortoise_backend_path(self) -> str:
        return "tortoise.backends.mysql"

    def tortoise_settings(self) -> dict:
        mysql_settings = {"database": self.settings["db_prefix"] + self.extension.label}
        if self.settings["user"]:
            mysql_settings["user"] = self.settings["user"]
        if self.settings["password"]:
            mysql_settings["password"] = self.settings["password"]
        if self.settings["host"]:
            mysql_settings["host"] = self.settings["host"]
        if self.settings["port"]:
            mysql_settings["port"] = self.settings["port"]
        return mysql_settings
