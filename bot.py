"""Pycord bot module"""
import discord
import pretty_errors
from discord import commands

from config.config import config

intents = discord.Intents.default()
intents.members = True # pylint: disable=assigning-non-slot
pretty_errors.activate()

bot = discord.Bot()

@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

bot.run(config.bot_token)
