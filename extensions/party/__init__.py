"""Party bot import module"""
from .party import Party

def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Party cog to bot.
    """
    bot.add_cog(Party(bot))
