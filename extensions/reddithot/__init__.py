"""Reddit bot import module"""
from .reddithot import RedditHot


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds RedditHot cog to bot.
    """
    bot.add_cog(RedditHot(bot))
