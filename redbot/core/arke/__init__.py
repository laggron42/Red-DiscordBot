from redbot.core.errors import CogLoadError

try:
    from tortoise import *
except ImportError as e:
    raise CogLoadError(
        "You need to install Red with the `arke` dependency to use this feature. "
        "Run `python3 -m pip install -U Red-DiscordBot[arke]`."
    )

from redbot.core.arke.manager import *
from redbot.core.arke.meta import *
from redbot.core.arke.backends import *
