"""Openai bot import module"""
from .openaichat import OpenAI

def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Chat cog to bot.
    """
    bot.add_cog(OpenAI(bot))
