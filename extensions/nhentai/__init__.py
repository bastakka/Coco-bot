"""nhentai bot import module"""
from .nhentai import Nhentai


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Nhentai cog to bot.
    """
    bot.add_cog(Nhentai(bot))
