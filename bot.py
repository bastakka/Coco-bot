"""Pycord bot module"""
from datetime import datetime

import discord
import pretty_errors
from colorama import Fore, init
from discord.ext import commands

from core.config import get_config
from core.logger import get_logger

init(autoreset=True)
pretty_errors.activate()
print(f"{Fore.YELLOW}[*] Coco loading...")
config = get_config()
logger = get_logger(__name__)
logger.info("Configuration & logger loaded")


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


logger.info("Coco started at %s", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
coco = commands.Bot(intents=intents, command_prefix=get_prefix, case_insensitive=True)
coco.remove_command("help")


@coco.event
async def on_ready() -> None:
    """Code that runs after bot establishes connection to discord servers.

    Primarly used to print status info.
    """
    print(f"{Fore.BLUE}[*] Pycord version: {discord.__version__}")
    print(f"{Fore.MAGENTA}[✓] Serving on:")
    for guild in coco.guilds:
        print(f"{Fore.MAGENTA}[✓] {guild.name} - {guild.id}")
    await coco.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="あさココLIVEニュース"
        )
    )
    print(f"{Fore.MAGENTA}------------------")
    login_message = f"Logged in as {coco.user.name}#{coco.user.discriminator}"
    logger.info(login_message)


if config.debug is False:

    @coco.event
    async def on_command_error(ctx: commands.Context, error) -> None:
        """Error handler which informs an user in a funny way."""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Which song, word, doujin... Am I a fucking genie or what".upper(),
                delete_after=10,
            )
            await ctx.message.delete(delay=10)
            await ctx.message.add_reaction("🤔")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("What does this even mean?", delete_after=10)
            await ctx.message.delete(delay=10)
            await ctx.message.add_reaction("🤔")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "Too fast buddy. Try again in {error.retry_after:.2f} seconds.",
                delete_after=10,
            )
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("An error occured.", delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Who are you to command me like that.", delete_after=10)
            await ctx.message.delete(delay=10)
        else:
            await ctx.send(f"An error occured in command {ctx.command}.\n{error}")
            raise error

    @coco.event
    async def on_error(event, *args, **kwargs) -> None:
        """Error handler for internal errors."""
        logger.error(
            "An error occured in %s with arguments %s from %s and kwargs %s",
            event,
            args[0].content if args else "none",
            args[0].author if args else "no one",
            kwargs,
        )


print(f"{Fore.YELLOW}[*] Extensions loading...")
for extension in config.extensions_enabled:
    try:
        coco.load_extension(f"extensions.{extension}")
        logger.info("Extension %s loaded", extension)
    except Exception as e:
        error_message = f"{extension.capitalize()} failed to load.\n{e}"
        logger.error(error_message)
print(
    f"{Fore.YELLOW}[✓] Enabled extensions: "
    + ", ".join(extension.split(".")[1] for extension in coco.extensions)
)
print(f"{Fore.YELLOW}[✗] Disabled extensions: " + ", ".join(config.extensions_disabled))

coco.run(config.bot_token)
