"""DiscordTogether bot commands cog module"""
from discord.ext import commands
from discord_together import DiscordTogether
from core.basecog import BaseCog


class Party(BaseCog):
    """Bot discord_together commands"""

    def cog_check(self, ctx: commands.Context) -> bool:
        """Check if the user is in a voice channel"""
        if ctx.author.voice is None:
            ctx.send("You must be in a voice channel to use this command.")
            return False
        return True

    @commands.command()
    async def party(self, ctx: commands.Context, activity: str = "youtube") -> None:
        """Creates link for discord together activity"""
        activities = [
            "youtube",
            "chess",
            "betreyal",
            "fishing",
            "letter-tile",
            "word-snack",
            "doodle-crew",
            "spellcast",
            "awkword",
            "checkers",
        ]
        if activity in activities:
            together_control = await DiscordTogether(self.config.bot_token)
            link = await together_control.create_link(
                ctx.author.voice.channel.id, activity
            )
            await ctx.send(f"Click the blue link!\n{link}")
            await together_control.close()
        else:
            await ctx.send(
                "Invalid activity\nAvailable activities: " + ", ".join(activities)
            )
