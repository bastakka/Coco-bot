"""nhentai bot commands cog module"""
import discord
from discord.ext import commands
from hentai import Hentai, Utils
from core import checks
from core.basecog import BaseCog
from .doujin import Doujin


def make_doujin_embed(doujin: Doujin) -> discord.Embed:
    """Make an embed from a Doujin object"""
    embed = discord.Embed(title=doujin.title, url=doujin.url, color=0xFF0000)
    embed.add_field(name="Artist", value=doujin.artist)
    embed.add_field(name="Language", value=doujin.languages)
    embed.add_field(name="Tags", value=doujin.tags, inline=False)
    if doujin.parodies:
        embed.add_field(name="Parody", value=doujin.parodies)
    embed.set_image(url=doujin.image_urls[0])
    embed.set_author(
        name="nhentai",
        url="https://nhentai.net",
        icon_url="attachment://logo-nhentai.png"
    )
    embed.set_footer(text=f"Uploaded on {doujin.date}")
    return embed


class Nhentai(BaseCog):
    """Bot nhentai commands cog"""

    @commands.check(checks.is_nsfw)
    @commands.command(name="numbers")
    async def _numbers(self, ctx: commands.Context, numbers) -> None:
        """Returns custom doujin embed from ID of doujin on nhentai"""
        try:
            numbers = int(numbers)
        except ValueError:
            await ctx.send("Those are not numbers buddy")
            return
        if Hentai.exists(numbers):
            doujin = Doujin(Hentai(numbers))
            embed = make_doujin_embed(doujin)
            img_author = discord.File(
                "assets/images/logos/logo-nhentai.png",
                filename="logo-nhentai.png",
            )
            await ctx.send(file = img_author, embed = embed)
        else:
            await ctx.send("You got the wrong numbers buddy")

    @commands.check(checks.is_nsfw)
    @commands.command()
    async def numbers_random(self, ctx: commands.Context) -> None:
        """Passes output of hentai.Utils random to _numbers command"""
        doujin = Utils.get_random_hentai()
        await ctx.invoke(self._numbers, doujin.id)

    @commands.check(checks.is_nsfw)
    @commands.command()
    async def numbers_search(self, ctx: commands.Context, *, query: str) -> None:
        """Searches for doujin by query and passes output to _numbers command"""
        doujins = Utils.search_by_query(query)
        for doujin in doujins:
            await ctx.invoke(self._numbers, doujin.id)
            return
