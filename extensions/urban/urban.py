"""Urban dictionary bot commands cog module"""
import json
from urllib.parse import quote as urlquote
from urllib.request import urlopen

import discord
from discord.ext import commands
from core.basecog import BaseCog

from .definition import Definition

UD_URL = "https://api.urbandictionary.com/v0/define?term="
UD_RANDOM = "https://api.urbandictionary.com/v0/random"


def _make_urbandict_embed(definition: Definition) -> discord.Embed:
    """Make an embed from a Definition object"""
    embed = discord.Embed(
        title=definition.term,
        url=definition.url,
        description=definition.description,
        color=0x00FF00,
    )
    embed.set_author(
        name="Urban Dictionary",
        url="https://www.urbandictionary.com/",
        icon_url="attachment://logo-urban-dictionary.png",
    )
    if definition.example:
        embed.add_field(name="Example", value=definition.example, inline=False)
    footer = f"Written by {definition.author} on {definition.date}"
    footer += f" | 👍 {definition.thumbs_up} 👎 {definition.thumbs_down}"
    embed.set_footer(text=footer)
    return embed


def _parse_postition(word: str) -> tuple:
    """Parse the position of a definition"""
    position = word.split()[-1]
    if position.startswith("#"):
        position_number = position[1:]
        if position_number.isdigit():
            word = word.replace(position, "")
            return word, int(position_number) - 1
        return word, -1
    return word, 0


def _get_urban_json(url: str) -> dict:
    """Get the json data from the urban dictionary api"""
    try:
        with urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {"list": []}


def _parse_urban_json(json_data: dict, position: int) -> dict:
    """Parse the json data from the urban dictionary api"""
    if json_data["list"] == []:
        return {}
    try:
        return json_data["list"][position]
    except IndexError:
        return {}


def _get_urban_definition(word: str, position: int) -> dict:
    """Get the urban dictionary definition for a word"""
    url = UD_URL + urlquote(word)
    if word == "random":
        url = UD_RANDOM
    json_data = _get_urban_json(url)
    return _parse_urban_json(json_data, position)


class Urban(BaseCog):
    """Bot urban dictionary related commands cog"""

    @commands.command()
    async def urban(self, ctx: commands.Context, *, word: str):
        """Returns a definition from urban dictionary"""
        word, position = _parse_postition(word)
        position = max(position, 0)

        definition = _get_urban_definition(word, position)
        if definition == {}:
            await ctx.send("No definition found or index out of range")
            return

        img_author = discord.File(
            "assets/images/logos/logo-urban-dictionary.png",
            filename="logo-urban-dictionary.png",
        )
        embed = _make_urbandict_embed(Definition(definition))
        await ctx.send(file=img_author, embed=embed)
