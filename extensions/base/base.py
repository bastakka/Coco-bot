"""Base bot commands cog module"""
import os
import sys
from datetime import datetime

import discord
from discord.ext import commands
from youtube_dl.utils import shell_quote
from core.basecog import BaseCog


def _make_embed(title, description=None, color=0xFFFF00) -> discord.Embed:
    """Make an embed"""
    embed = discord.Embed(
        title=title, description=description if description else "", color=color
    )
    return embed


class Base(BaseCog):
    """Bot base commands and listeners class"""

    def __init__(self, bot: commands.Bot) -> None:
        """Base class init with time of boot."""
        super().__init__(bot)
        self.time_of_boot = datetime.now().replace(microsecond=0)

    @commands.Cog.listener()
    async def on_message(self, ctx: commands.Context) -> None:
        """On message listener reacting to funny numbers."""
        split_message = ctx.content.split()
        if "69" in split_message:
            await ctx.channel.send("Nice")  # Nice
        elif "420" in split_message:
            await ctx.channel.send("Blaze it")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """On guild join listener for logging"""
        self.logger.info("Joined guild %s - %i", guild.name, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """On guild remove listener for logging"""
        self.logger.info("Left guild %s - %i", guild.name, guild.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """On member join listener for logging"""
        self.logger.info("%s joined %s", member.nick, member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """On member remove listener for logging"""
        self.logger.info("%s left %s", member.nick, member.guild)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None:
        """On member ban listener for logging"""
        self.logger.info("%s banned %s", user.name, guild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        """On member unban listener for logging"""
        self.logger.info("%s was unbanned from %s", user.name, guild)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.TextChannel) -> None:
        """On guild channel create listener for logging"""
        self.logger.info("%s created channel %s", channel.guild, channel.name)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel) -> None:
        """On guild channel delete listener for logging"""
        self.logger.info("%s deleted channel %s", channel.guild, channel.name)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """On message delete listener for logging in log channel"""
        if message.guild is None:
            return
        if message.guild.id == self.config.bot_log_channel_id:
            self.logger.info(
                "%s's message was deleted. Content:\n'%s'",
                message.author,
                message.content,
            )

    @commands.cooldown(rate=1, per=5, type=commands.BucketType.channel)
    @commands.command()
    async def uptime(self, ctx) -> None:
        """Uptime command"""
        time_now = datetime.now().replace(microsecond=0)
        delta = time_now - self.time_of_boot
        embed = _make_embed("Uptime")
        embed.add_field(
            name="Boot time", value=self.time_of_boot.strftime("%d/%m/%Y %H:%M:%S")
        )
        embed.add_field(name="Uptime", value=str(delta))
        await ctx.send(embed=embed)

    @commands.cooldown(rate=1, per=2, type=commands.BucketType.channel)
    @commands.command()
    async def ping(self, ctx) -> None:
        """Ping command"""
        embed = _make_embed("Pong!")
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms")
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def shutdown(self, ctx) -> None:
        """Shutdown command"""
        time_now = datetime.now().replace(microsecond=0)
        delta = time_now - self.time_of_boot
        embed = _make_embed("Shutting down...")
        embed.add_field(name="Uptime", value=str(delta))
        await ctx.send(embed=embed)
        await self.bot.close()
        sys.exit(0)

    @commands.is_owner()
    @commands.command()
    async def restart(self, ctx) -> None:
        """Restart command"""
        time_now = datetime.now().replace(microsecond=0)
        delta = time_now - self.time_of_boot
        embed = _make_embed("Restarting...")
        embed.add_field(name="Uptime", value=str(delta))
        await ctx.send(embed=embed)
        await self.bot.change_presence(activity=discord.Game(name="Restarting..."))
        sys.stdout.flush()
        os.execv(sys.executable, ["python"] + sys.argv)

    @commands.command()
    async def reload_config(self, ctx: commands.Context) -> None:
        """Bot command used for reloading config on the go.
        Usefull to not waste time restarting entire bot for some changes in config.

        Changes in "bot" category are still recommended to be followed up by restart.
        Outputs successfull reload to channel, where command was invoked.
        """
        self.config.reload()
        await ctx.send("🔁 Config reloaded.", delete_after=10)
        await ctx.message.delete(delay=10)
