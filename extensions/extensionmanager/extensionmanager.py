"""Extensions bot commands cog module"""
import discord
from discord.ext import commands
from core.basecog import BaseCog

def make_extensions_embed(config):
    """Creates an embed for the extensions list"""
    enabled = ", ".join(extension for extension in config.extensions_enabled)
    disabled = ", ".join(extension for extension in config.extensions_disabled)
    embed = discord.Embed(title="Extensions", color=0x000000)
    embed.add_field(name="Enabled", value=enabled, inline=False)
    embed.add_field(name="Disabled", value=disabled, inline=False)
    return embed

class ExtensionManager(BaseCog):
    """Extension manager cog class"""

    @commands.is_owner()
    @commands.command()
    async def list_extensions(self, ctx):
        """Lists all extensions"""
        await ctx.send(embed=make_extensions_embed(self.config))

    @commands.is_owner()
    @commands.command()
    async def enable_extension(self, ctx, *, extensions: str):
        """Enable extension(s) separated by space"""
        for extension in extensions.split():
            extension = extension.lower()
            if extension in self.config.extensions_enabled:
                await ctx.send(f"Extension `{extension}` already enabled")
                continue
            if extension in self.config.extensions_disabled:
                try:
                    self.bot.load_extension(f"extensions.{extension}")
                    self.config.enable_extension(extension)
                    self.logger.info("Enabled extension `%s`", extension)
                    await ctx.send(f"Enabled extension `{extension}`")
                    continue
                except Exception as e:
                    self.logger.error("Failed to enable extension `%s`", extension)
                    await ctx.send(f"Error enabling extension `{extension}`: {e}")
                    continue
            await ctx.send(f"Extension `{extension}` not found")

    @commands.is_owner()
    @commands.command()
    async def disable_extension(self, ctx, *, extensions: str):
        """Disable extension(s) separated by space"""
        for extension in extensions.split():
            extension = extension.lower()
            if extension in self.config.extensions_disabled:
                await ctx.send(f"Extension `{extension}` already disabled")
                continue
            if extension in self.config.extensions_enabled:
                try:
                    self.bot.unload_extension(f"extensions.{extension}")
                    self.config.disable_extension(extension)
                    self.logger.info("Disabled extension `%s`", extension)
                    await ctx.send(f"Disabled extension `{extension}`")
                    continue
                except Exception as e:
                    self.logger.error("Failed to disable extension `%s`", extension)
                    await ctx.send(f"Error disabling extension `{extension}`: {e}")
                    continue
            await ctx.send(f"Extension `{extension}` not found")

    @commands.is_owner()
    @commands.command()
    async def reload_extension(self, ctx, *, extensions: str):
        """Reload extension(s) separated by space"""
        for extension in extensions.split():
            extension = extension.lower()
            if extension in self.config.extensions_enabled:
                try:
                    self.bot.reload_extension(f"extensions.{extension}")
                    self.logger.info("Reloaded extension `%s`", extension)
                    await ctx.send(f"Reloaded extension `{extension}`")
                    continue
                except Exception as e:
                    self.logger.error("Failed to reload extension `%s`", extension)
                    await ctx.send(f"Error reloading extension `{extension}`: {e}")
            if extension in self.config.extensions_disabled:
                await ctx.send(f"Extension `{extension}` is disabled")
                continue
            await ctx.send(f"Extension `{extension}` not found")
