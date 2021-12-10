"""Commands custom checks"""

from discord.ext import commands

def is_nsfw(ctx: commands.Context) -> bool:
    """Returns bool of nsfw status in channel of message"""
    if ctx.guild is None:
        return True
    return ctx.channel.is_nsfw()