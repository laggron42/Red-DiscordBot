import logging
import importlib.util

from typing import TYPE_CHECKING, Type, List

from tortoise import Tortoise
from tortoise.connection import connections

from redbot.core.arke.meta import ArkeMetaBase
from redbot.core.arke.backends import get_backend, BackendType

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from tortoise.backends.base.client import BaseDBAsyncClient
    from redbot.core.arke.backends import ArkeBackend

log = logging.getLogger("red.arke")
arke_instance = None


class ArkeExtension:
    connection: "BaseDBAsyncClient"
    backend: "ArkeBackend"

    def __init__(self, extension: "ModuleSpec", meta: Type[ArkeMetaBase]):
        self.extension = extension
        self.meta = meta()
        if importlib.util.find_spec("modules", extension):
            self.meta.models_path += ("modules",)
        if self.meta.backend_requirement:
            self.backend = get_backend(self.meta.backend_requirement)(self)
        else:
            self.backend = None
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
            module._meta.db_table = self.meta.table_prefix + module._meta.db_table
        log.debug(
            f"Initialized {len(Tortoise.apps[self.label])} "
            f"models from extension {self.extension.name}"
        )

    def __hash__(self):
        return hash(self.extension)


class RedArkeManager:
    def __init__(self):
        self._extensions: List[ArkeExtension] = []
        self.preferred_backend: BackendType = BackendType.SQLITE
        connections._db_config = {}
        Tortoise._init_routers()
        Tortoise._inited = True
        log.debug(f"Arke initialized. Preferred backend: {self.preferred_backend.name}")

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
        if not arke_ext.backend:
            arke_ext.backend = get_backend(self.preferred_backend)(arke_ext)

        # Tortoise was designed for apps where the full config is known before starting all the
        # backends together. To properly support Red's modularity, Tortoise.init() is not called
        # and we try to start backends one by one, mimicking Tortoise's normal behaviour
        connections._db_config[arke_ext.label] = {
            "engine": arke_ext.backend.tortoise_backend_path,
            "credentials": arke_ext.backend.tortoise_settings(),
        }
        connection = connections.get(arke_ext.label)
        await connection.create_connection(with_db=True)
        log.debug(f"Created db connection to {arke_ext.backend} for {arke_ext.label}")
        arke_ext.connection = connection

        await arke_ext.init()
        Tortoise._build_initial_querysets()
        self._extensions.append(arke_ext)

        await Tortoise.generate_schemas()  # TODO: remove, use migrations instead
        await arke_ext.meta.post_init()
        return True

    async def unregister_extension(self, extension: ArkeExtension):
        await extension.meta.pre_close()
        await extension.connection.close()
        log.debug(f"Closed db connection to {extension.backend} for {extension.label}")
        await extension.meta.post_close()
        self._extensions.remove(extension)
