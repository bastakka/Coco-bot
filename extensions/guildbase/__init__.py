"""Guildbase bot import module"""
from .guildbase import GuildBase

def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Base cog to bot.
    """
    bot.add_cog(GuildBase(bot))
