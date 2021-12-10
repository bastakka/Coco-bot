"""Base bot import module"""
from .base import Base

def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Base cog to bot.
    """
    bot.add_cog(Base(bot))
