from typing import Optional, Sequence

from redbot.core.arke.enums import Backend


class ArkeMetaBase:
    """
    Set up your package for the Arke database system.

    You must subclass this class and name it ``ArkeMeta``. It must be importable from the package.

    Attributes
    ----------
    app_label: str
        A custom label for your application. Defaults to the module name.
    database_path: str
        The folder where the database will be saved. Defaults to the app label
    engine_requirement: Optional[Backend]
        You may add a backend as a hard requirement, which ensures your cog will load
        with the database you specified. If the database is not installed, the package will not
        load. If you omit this, any backend will be accepted (most likely SQLite).
    table_prefix: str
        A prefix for all of your table names. Can be useful to avoid conflicts.
    models_path: Sequence[str]
        A list of paths where models can be found. By default, Arke will look in the package itself
        (anything imported in ``__init__.py``) and ``models`` (a python file or a submodule). Any
        model not importable from these paths will not be loaded.
    discord_models: bool
        Specify if you want to enable Discord models in your database (allows relations with the
        supported discord models). Set to `False` to prevent creating these models. Defaults to
        `True`.
    """

    app_label: str = None
    database_path: str = None
    engine_requirement: Optional[Backend] = None
    table_prefix: str = ""
    models_path: Sequence[str] = ()
    discord_models: bool = True

    async def pre_init(self):
        pass

    async def post_init(self):
        pass

    async def pre_close(self):
        pass

    async def post_close(self):
        pass
