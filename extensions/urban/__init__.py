"""Urban bot import module"""
from .urban import Urban


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds OpenAI cog to bot.
    """
    bot.add_cog(Urban(bot))
