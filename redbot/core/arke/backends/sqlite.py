from redbot.core.data_manager import cog_data_path
from redbot.core.arke.backends.base import ArkeBackend

from typing import TypedDict


class Settings(TypedDict):
    pass


class SQLiteBackend(ArkeBackend[Settings]):
    @staticmethod
    def prompt_backend_settings() -> dict:
        return {}

    @property
    def tortoise_backend_path(self) -> str:
        return "tortoise.backends.sqlite"

    def tortoise_settings(self) -> dict:
        return {
            "file_path": cog_data_path(None, raw_name=self.extension.data_path) / "arke.sqlite3"
        }
