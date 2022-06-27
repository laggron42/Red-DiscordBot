from redbot.core.errors import CogLoadError

try:
    import tortoise
except ImportError as e:
    raise CogLoadError(
        "You need to install Red with the `arke` dependency to use this feature. "
        "Run `python3 -m pip install -U Red-DiscordBot[arke]`."
    )
