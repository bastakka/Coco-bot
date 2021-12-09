"""Module for base cog class."""
import time
from discord.ext import commands
from core.logger import get_logger
from core.config import get_config


class BaseCog(commands.Cog):
    """Base cog class."""

    def __init__(self, bot):
        """Init base cog class."""
        self.bot = bot
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__, self.config.debug)

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """Code that runs before invoked command.

        Used for logging chat commands.
        """
        message = f"{ctx.author.name}#{ctx.author.discriminator} issued the command `{ctx.command}`"
        chat = ctx.guild.name if ctx.guild else "Direct message"
        log_message = f"{message} in {chat}."
        self.logger.info(log_message)
        log_channel = self.bot.get_channel(int(self.config.bot_log_channel_id))
        await log_channel.send(log_message)
        ctx.start = time.time()

    async def cog_after_invoke(self, ctx: commands.Context) -> None:
        """Code that runs after invoked command.

        Used for logging how long command took to complete.
        """
        end = time.time()
        delta = end - ctx.start
        log_message = f"Command {ctx.command} successfully completed after"
        log_message += f" {format(delta, '.2f')} seconds."
        self.logger.info(log_message)
        log_channel = self.bot.get_channel(int(self.config.bot_log_channel_id))
        await log_channel.send(log_message)
