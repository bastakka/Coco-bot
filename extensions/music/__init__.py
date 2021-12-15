"""Music bot import module"""
from .music import Music


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Music cog to bot.
    """
    bot.add_cog(Music(bot))
