"""Roles bot import module"""
from .roles import Roles


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Roles cog to bot.
    """
    bot.add_cog(Roles(bot))
