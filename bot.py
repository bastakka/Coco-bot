"""Pycord bot module"""
import discord
import pretty_errors
from colorama import init, Fore
from discord.ext import commands

from config.config import config

init(autoreset=True)
intents = discord.Intents.default()
intents.members = True # pylint: disable=assigning-non-slot
pretty_errors.activate()

async def get_prefix(bot, message):
    """Gets specified prefix for guild if set.
    If not set, prefix defaults to "coco ".

    Returns when_mentioned_or(prefix) function needed for pycord.
    """
    if message.guild is None:
        prefix = "coco "
    elif str(message.guild.id) not in config.prefixes:
        config.prefixes[str(message.guild.id)] = "coco "
        config.save()
        prefix = "coco "
    else:
        prefix = config.prefixes.get(str(message.guild.id))
    return commands.when_mentioned_or(prefix)(bot, message)

coco = commands.Bot(
    intents=intents,
    command_prefix=get_prefix,
    case_insensitive=True
)

@coco.event
async def on_ready() -> None:
    """Code that runs after bot establishes connection to discord servers.

    Primarly used to print status info.
    """
    print(f"{Fore.BLUE}[*] Pycord version: {discord.__version__}")
    print(f"[*] Logged in as: {coco.user.name} - {coco.user.id}\n")
    print("[*] Serving on:")
    for guild in coco.guilds:
        print(f"[*] {guild.name} - {guild.id}")
    await coco.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="あさココLIVEニュース"))
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
            await ctx.send("Which song, word, extension... Am I a fucking genie or what".upper(),
                delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.BadArgument):
            await ctx.send("What does this even mean?", delete_after=10)
            await ctx.message.delete(delay=10)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Too fast buddy. Try again in {error.retry_after:.2f} seconds.",
                delete_after=10)
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
        """Error handler for internal errors.

        Outputs error to log channel defined in config.
        """
        await coco.get_channel(
            int(config.bot_log_channel_id)).send(f"An error occured.\n{event}\n{args}\n{kwargs}")

@coco.before_invoke
async def before_invoke(ctx: commands.Context) -> None:
    """Code that runs before invoked command.

    Used for logging in both log_channel and standart output.
    TODO: Use standard logger
    """
    log_channel = coco.get_channel(int(config.bot_log_channel_id))
    message = f"{ctx.author.name}#{ctx.author.discriminator} issued the command `{ctx.command}`"
    if ctx.guild is None:
        print(f"{Fore.BLACK}[*] " + message + " in DMs")
        await log_channel.send(message + " in DMs")
    else:
        print(f"{Fore.BLACK}[*] " + message + f" in {ctx.guild.name}")
        await log_channel.send(message + f" in {ctx.guild.name}")

@commands.check(lambda ctx: ctx.guild is None)
@coco.command()
async def reload_config(ctx: commands.Context) -> None:
    """Bot command used for reloading config on the go.
    Usefull to not waste time restarting entire bot for some changes in config.

    Changes in "bot" category are still recommended to be followed up by restart.

    Outputs successfull reload to channel, where command was invoked.
    """
    config.reload()
    await ctx.send("Config successfully reloaded.", delete_after=10)
    await ctx.message.delete(delay=10)

print(f"{Fore.GREEN}[*] Loading complete!\n" + "=" * 50)
coco.run(config.bot_token)
