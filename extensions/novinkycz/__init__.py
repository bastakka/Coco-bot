"""Seznam bot import module"""
from .novinkycz import Novinkycz


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Novinkycz cog to bot.
    """
    bot.add_cog(Novinkycz(bot))
