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


class PostgreSQLBackend(ArkeBackend[Settings]):
    @staticmethod
    def prompt_backend_settings() -> dict:
        unixmsg = ""
        if sys.platform != "win32":
            unixmsg = (
                " - Common directories for PostgreSQL Unix-domain sockets (/run/postgresql, "
                "/var/run/postgresl, /var/pgsql_socket, /private/tmp, and /tmp),\n"
            )
        host = (
            input(
                f"Enter the PostgreSQL server's address.\n"
                f"If left blank, Red will try the following, in order:\n"
                f" - The PGHOST environment variable,\n{unixmsg}"
                f" - localhost.\n"
                f"> "
            )
            or None
        )

        print(
            "Enter the PostgreSQL server port.\n"
            "If left blank, this will default to either:\n"
            " - The PGPORT environment variable,\n"
            " - 5432."
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
                "If left blank, this will default to either:\n"
                " - The PGUSER environment variable,\n"
                " - The OS name of the user running Red (ident/peer authentication).\n"
                "> "
            )
            or None
        )

        passfile = r"%APPDATA%\postgresql\pgpass.conf" if sys.platform == "win32" else "~/.pgpass"
        password = getpass.getpass(
            f"Enter the PostgreSQL server password. The input will be hidden.\n"
            f"  NOTE: If using ident/peer authentication (no password), enter NONE.\n"
            f"When NONE is entered, this will default to:\n"
            f" - The PGPASSWORD environment variable,\n"
            f" - Looking up the password in the {passfile} passfile,\n"
            f" - No password.\n"
            f"> "
        )
        if password == "NONE":
            password = None

        return {"host": host, "port": port, "user": user, "password": password}

    @property
    def tortoise_backend_path(self) -> str:
        return "tortoise.backends.asyncpg"
        # Tortoise also supports PostgreSQL through the psycopg backend, maybe offer to switch?

    def tortoise_settings(self) -> dict:
        postgresql_settings = {"database": self.settings["db_prefix"] + self.extension.label}
        if self.settings["user"]:
            postgresql_settings["user"] = self.settings["user"]
        if self.settings["password"]:
            postgresql_settings["password"] = self.settings["password"]
        if self.settings["host"]:
            postgresql_settings["host"] = self.settings["host"]
        if self.settings["port"]:
            postgresql_settings["port"] = self.settings["port"]
        return postgresql_settings
