from typing import TYPE_CHECKING, Generic, TypedDict, TypeVar

if TYPE_CHECKING:
    from redbot.core.arke.core import ArkeExtension

Settings = TypeVar("Settings", bound=TypedDict)


class ArkeBackend(Generic[Settings]):
    """
    Base class for Arke backends.

    The compatible backends are the ones supported by Tortoise which does all the work, however
    additional code is required on our end for things like the settings.
    """

    def __init__(self, extension: "ArkeExtension", settings: Settings = {}):
        self.extension = extension
        self.settings = settings

    def __str__(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def prompt_backend_settings() -> dict:
        """
        Returns a list of settings specific to this backend.
        """
        raise NotImplementedError

    @property
    def tortoise_backend_path(self) -> str:
        """
        Path to the tortoise backend.
        """
        raise NotImplementedError

    def tortoise_settings() -> dict:
        """
        The settings dictionnary passed to Tortoise.
        """
        raise NotImplementedError
