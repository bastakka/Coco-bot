"""Pycord bot module"""
import time
import discord
import pretty_errors
from colorama import Fore, init
from discord.ext import commands

from config.config import get_config
from logs.logger import get_logger

init(autoreset=True)
pretty_errors.activate()
print(f"{Fore.YELLOW}[*] Coco loading...")
config = get_config()
print(f"{Fore.GREEN}[✓] Config loaded!")
logger = get_logger(__name__)
print(f"{Fore.GREEN}[✓] Logging enabled!")

intents = discord.Intents.default()
intents.members = True  # pylint: disable=assigning-non-slot


async def get_prefix(bot, message):
    """Gets specified prefix for guild if set.
    If not set, prefix defaults to "coco ".

    Returns when_mentioned_or(prefix) function needed for pycord.
    """
    if message.guild is None:
        prefix = config.default_prefix
    elif str(message.guild.id) not in config.prefixes:
        config.prefixes[str(message.guild.id)] = config.default_prefix
        config.save()
        prefix = config.default_prefix
    else:
        prefix = config.prefixes.get(str(message.guild.id))
    return commands.when_mentioned_or(prefix)(bot, message)


coco = commands.Bot(intents=intents, command_prefix=get_prefix, case_insensitive=True)


@coco.event
async def on_ready() -> None:
    """Code that runs after bot establishes connection to discord servers.

    Primarly used to print status info.
    """
    print(f"{Fore.BLUE}[*] Pycord version: {discord.__version__}")
    print(f"[✓] Logged in as: {coco.user.name} - {coco.user.id}\n")
    print("[✓] Serving on:")
    for guild in coco.guilds:
        print(f"[✓] {guild.name} - {guild.id}")
    await coco.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="あさココLIVEニュース"
        )
    )
    print(50 * "=")


if config.debug is False:

    @coco.event
    async def on_command_error(ctx, error) -> None:
        """
        Error handler which informs an user in a funny way.
        """
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Which song, word, extension... Am I a fucking genie or what".upper(),
                delete_after=10,
            )
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("What does this even mean?", delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "Too fast buddy. Try again in {error.retry_after:.2f} seconds.",
                delete_after=10,
            )
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("An error occured.", delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Who are you to command me like that.", delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Who are you to command me like that.", delete_after=10)
            await ctx.message.delete(delay=10)
        else:
            await ctx.send(f"An error occured.\n{error}")
            raise error

    @coco.event
    async def on_error(event, *args, **kwargs) -> None:
        """Error handler for internal errors."""
        logger.error(
            "An error occured in %s with arguments %s and kwarguments %s",
            event,
            args,
            kwargs,
        )


@coco.before_invoke
async def before_invoke(ctx: commands.Context) -> None:
    """Code that runs before invoked command.

    Used for logging
    """
    log_channel = coco.get_channel(int(config.bot_log_channel_id))
    message = f"{ctx.author.name}#{ctx.author.discriminator} issued the command `{ctx.command}`"
    chat = ctx.guild.name if ctx.guild else "Direct message"
    logger.info("%s in %s.", message, chat)
    await log_channel.send(f"{message} in {chat}.")
    ctx.start = time.time()


@coco.after_invoke
async def after_invoke(ctx: commands.Context) -> None:
    """Code that runs after invoked command.

    Used for logging how long command took to complete.
    """
    end = time.time()
    log_channel = coco.get_channel(int(config.bot_log_channel_id))
    message = f"Command {ctx.command} successfully completed after"
    delta = end - ctx.start
    logger.info("%s %f seconds.", message, delta)
    await log_channel.send(f"{message} {delta} seconds.")


# @commands.check(lambda ctx: ctx.guild is None)
@coco.command()
async def reload_config(ctx: commands.Context) -> None:
    """Bot command used for reloading config on the go.
    Usefull to not waste time restarting entire bot for some changes in config.

    Changes in "bot" category are still recommended to be followed up by restart.

    Outputs successfull reload to channel, where command was invoked.
    """
    config.reload()
    await ctx.send("🔁 Config reloaded.", delete_after=10)
    await ctx.message.delete(delay=10)

print(f"{Fore.YELLOW}[*] Loading extensions...")
print(f"{Fore.YELLOW}[✓] Enabled extensions: " + ", ".join(config.extensions_enabled))
print(f"{Fore.YELLOW}[✗] Disabled extensions: " + ", ".join(config.extensions_disabled))

coco.run(config.bot_token)
