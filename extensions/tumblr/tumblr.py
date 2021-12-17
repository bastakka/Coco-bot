"""Tumblr bot commands and loop cog module"""
import json
import os
import discord
from discord.ext import commands, tasks
from pytumblr import TumblrRestClient
from core.basecog import BaseCog

async def _make_tumblr_embed() -> discord.Embed:
    embed = discord.Embed()
    return embed

class Tumblr(BaseCog):
    """Bot Tumblr commands and loop"""

    def __init__(self, bot) -> None:
        