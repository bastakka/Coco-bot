"""Module for base cog class."""
import time

from discord.ext import commands

from core.config import get_config
from core.logger import get_logger


class BaseCog(commands.Cog):
    """Base cog class."""

    def __init__(self, bot):
        """Init base cog class."""
        self.bot = bot
        self.config = get_config()
        self.logger = get_logger(self.__class__.__name__, self.config.debug)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Log when bot is ready."""
        self.logger.info("%s cog loaded succesfully", self.__class__.__name__)

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """Code that runs before invoked command.

        Used for logging chat commands.
        """
        author = ctx.author
        message = f"{author.name}#{author.discriminator} issued the command `{ctx.command.name}`"
        chat = ctx.guild.name if ctx.guild else "Direct message"
        log_message = f"{message} in {chat}."
        self.logger.debug(log_message)
        ctx.start = time.time()

    async def cog_after_invoke(self, ctx: commands.Context) -> None:
        """Code that runs after invoked command.

        Used for logging how long command took to complete.
        """
        end = time.time()
        delta = end - ctx.start
        log_message = f"Command {ctx.command.name} successfully completed after"
        log_message += f" {format(delta, '.2f')} seconds."
        self.logger.debug(log_message)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs) -> None: # pylint: disable=unused-argument
        """Error handler for internal errors."""
        self.logger.error(
            "An error occured in %s with arguments %s in extension %s",
            event,
            args,
            self.__class__.__name__
        )
