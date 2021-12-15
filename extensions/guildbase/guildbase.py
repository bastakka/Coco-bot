"""Guildbase bot commands cog module"""
from discord.ext import commands
from core.basecog import BaseCog


class GuildBase(BaseCog):
    """Bot base commands and listeners class"""

    @commands.cooldown(rate=1, per=20.0, type=commands.BucketType.channel)
    @commands.is_owner()
    @commands.command()
    async def guilds(self, ctx: commands.Context) -> None:
        """List all guilds the bot is in."""
        message = "```"
        for guild in self.bot.guilds:
            message += f"{guild.name} ({guild.id}) members: {guild.member_count}\n"
        message += "```"
        await ctx.send(message)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def setprefix(self, ctx, new_prefix: str) -> None:
        """Set prefix for guild command"""
        if new_prefix == "":
            await ctx.send("Prefix can't be empty!")
            return
        self.config.prefixes[str(ctx.guild.id)] = new_prefix
        self.config.save()
        await ctx.send(f"Prefix set to `{new_prefix}`")
