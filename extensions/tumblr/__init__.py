"""Tumblr bot cog import module"""
from .tumblr import Tumblr


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Tumblr cog to bot.
    """
    bot.add_cog(Tumblr(bot))
