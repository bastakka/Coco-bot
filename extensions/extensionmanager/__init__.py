"""nhentai bot import module"""
from .extensionmanager import ExtensionManager


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds ExtensionManager cog to bot.
    """
    bot.add_cog(ExtensionManager(bot))
