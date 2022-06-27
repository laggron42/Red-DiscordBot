import logging
import importlib.util

from typing import TYPE_CHECKING, Type, List

from tortoise import Tortoise
from tortoise.connection import connections

from redbot.core.data_manager import cog_data_path
from redbot.core.arke.meta import ArkeMetaBase
from redbot.core.arke.enums import Backend

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from tortoise.backends.base.client import BaseDBAsyncClient

log = logging.getLogger("red.arke.core")
arke_instance = None


class ArkeExtension:
    connection: "BaseDBAsyncClient"

    def __init__(self, extension: "ModuleSpec", meta: Type[ArkeMetaBase]):
        self.extension = extension
        self.meta = meta()
        if importlib.util.find_spec("modules", extension):
            self.meta.models_path += ("modules", )
        self.label = self.meta.app_label or self.extension.name

    @property
    def data_path(self):
        return self.meta.database_path or self.label

    @property
    def models_path(self):
        return self.meta.models_path

    async def init(self):
        await self.meta.pre_init()
        paths = (self.extension.name,) + self.meta.models_path
        Tortoise.init_models(paths, app_label=self.label)
        for module in Tortoise.apps[self.label].values():
            module._meta.default_connection = self.label
        log.debug(
            f"Initialized {len(Tortoise.apps[self.label])} "
            f"models from module {self.extension.name}"
        )
        await self.meta.post_init()

    def __hash__(self):
        return hash(self.extension)


class RedArkeManager:
    def __init__(self):
        self._extensions: List[ArkeExtension] = []
        self.preferred_backend: Backend = Backend.sqlite
        self._init_routers: bool = False
        connections._db_config = {}
        log.debug(f"Arke initialized. Preferred backend: {self.preferred_backend}")

    @classmethod
    @property
    def instance(cls):
        global arke_instance
        if not arke_instance:
            arke_instance = cls()
        return arke_instance

    async def register_extension(self, extension: "ModuleSpec") -> bool:
        lib = extension.loader.load_module()
        if hasattr(lib, "arke_meta"):
            meta = lib.arke_meta
            attr = "arke_meta"
        elif hasattr(lib, "ArkeMeta"):
            meta = lib.ArkeMeta
            attr = "arke_meta"
        else:
            del lib
            return False
        if not issubclass(meta, ArkeMetaBase):
            raise TypeError(
                f"The {attr} attribute in your package must subclass redbot.core.arke.ArkeMetaBase"
            )

        arke_ext = ArkeExtension(extension, meta)
        connections._db_config[arke_ext.label] = {
            "engine": self.preferred_backend.value,
            "credentials": {
                "file_path": cog_data_path(raw_name=arke_ext.data_path) / "arke.sqlite3"
            },
        }
        connection = connections.get(arke_ext.label)
        log.debug(f"Creating db connection to {self.preferred_backend} for {arke_ext.label}")
        await connection.create_connection(with_db=True)
        arke_ext.connection = connection
        await arke_ext.init()
        Tortoise._build_initial_querysets()
        self._extensions.append(arke_ext)
        if not self._init_routers:
            Tortoise._init_routers()
            log.debug("Initialized routers")
            self._init_routers = True
        Tortoise._inited = True
        await Tortoise.generate_schemas()
        return True

    async def unregister_extension(self, extension: ArkeExtension):
        await extension.meta.pre_close()
        await extension.connection.close()
        await extension.meta.post_close()
        self._extensions.remove(extension)
