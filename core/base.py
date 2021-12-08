"""Base bot commands cog module"""
import datetime
import os
import sys

import discord
from discord.ext import commands
from core import checks
from core.config import config


class Base(commands.Cog):
    """Bot base commands class"""

    def __init__(self, bot: commands.Bot) -> None:
        """Base class init with time of boot."""
        self.bot = bot
        self.time_of_boot = datetime.datetime.now().replace(microsecond=0)

    @commands.Cog.listener()
    async def on_message(self, ctx: commands.Context) -> None:
        """On message listener reacting to funny numbers."""
        split_message = ctx.content.split()
        if "69" in split_message:
            await ctx.channel.send("Nice")  # Nice
        elif "420" in split_message:
            await ctx.channel.send("Blaze it")

    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.channel)
    @commands.command()
    async def uptime(self, ctx: commands.Context) -> None:
        """Bot uptime command with cooldown of 1 time per 10 seconds in one guild channel.

        Returns discord embed with bot time of boot and uptime.
        """
        time_now = datetime.datetime.now().replace(microsecond=0)
        uptime = time_now - self.time_of_boot
        embed = discord.Embed(title="Uptime", color=0xffff00)
        embed.add_field(name="Boot", value=str(self.time_of_boot))
        embed.add_field(name="Uptime", value=str(uptime))
        await ctx.send(embed=embed, delete_after=10)
        await ctx.message.delete(delay=10)

    @commands.cooldown(rate=5, per=20.0, type=commands.BucketType.channel)
    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """"Bot ping command with cooldown of 5 times per 20 seconds in one guild channel.

        Returns discord.py generated bot latency.
        """
        await ctx.send(f"pong: **{self.bot.latency}s**")

    @commands.check(checks.is_bot_owner)
    @commands.command()
    async def shutdown(self, ctx: commands.Context) -> None:
        """Bot shutdown command usable only by predefined bot owner.

        Closes bot's connection with discord servers and exits.
        """
        await ctx.send("Finally I get to sleep...", delete_after=10)
        await ctx.message.delete(delay=10)
        await self.bot.close()

    @commands.check(checks.is_bot_owner)
    @commands.command()
    async def restart(self, ctx: commands.Context) -> None:
        """Bot restart command usable only by predefined bot owner.

        Closes bot's connection with discord and openes new instance of itself.
        """
        await ctx.send("Restarting...", delete_after=10)
        await ctx.message.delete(delay=10)
        await self.bot.close()
        sys.stdout.flush()
        os.execv(sys.executable, ['python3'] + sys.argv)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx: commands.Context, new_prefix: str) -> None:
        """Bot prefix change command for guilds usable only by users with administrator permissions.

        Takes string value of new prefix. Checks if string is not empty.

        If string is not empty, saves new prefix to configuration file with immidiate effect.
        """
        if new_prefix == "":
            await ctx.send("Prefix cannot be empty", delete_after=10)
            await ctx.message.delete(delay=10)
        config.prefixes[str(ctx.guild.id)] = new_prefix
        config.save()
        await ctx.send(f"Prefix changed to `{new_prefix}`.")

    @commands.check(checks.is_bot_owner)
    @commands.cooldown(rate=1, per=20.0, type=commands.BucketType.channel)
    @commands.command()
    async def guilds(self, ctx: commands.Context) -> None:
        """Bot list serving guilds command usable only by predefined bot owner.

        Loads all serving guilds from bot and sends them as a message back.
        """
        message = "```"
        for guild in self.bot.guilds:
            message += f"{guild.name} ({guild.id}) members: {guild.member_count}\n"
        message += "```"
        await ctx.send(message, delete_after=10)
        await ctx.message.delete(delay=10)


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Base cog to bot.
    """
    bot.add_cog(Base(bot))
