"""Module with Song class for voice state class"""
import discord
from discord.ext import commands
from .ytdlsource import YTDLSource

class Song:
    """Class for Song objects"""

    __slots__ = ("source", "requester", "title", "url")

    def __init__(self, source: YTDLSource):
        """Initializes the Song object"""
        self.source = source
        self.requester = source.requester
        self.title = source.title
        self.url = source.url

    def make_song_embed(self) -> discord.Embed:
        """Returns an embed for the song"""
        embed = discord.Embed(title=f"{self.source.title}", url=f"{self.source.url}")
        embed.set_thumbnail(url=f"{self.source.thumbnail}")
        embed.add_field(name="Duration", value=f"{self.source.duration}")
        embed.add_field(
            name="Uploader",
            value=f"[{self.source.uploader}]({self.source.uploader_url})",
        )
        embed.add_field(name="Upload date", value=f"{self.source.upload_date}")
        embed.set_footer(
            text=f"Requested by {self.requester.display_name}"
        )
        return embed