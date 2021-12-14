"""Module with Song and SongQueue classes for music cog"""
import asyncio
import itertools
import random
from typing import Union

import discord

from .ytdlsource import YTDLSource


class Song:
    """Class for Song objects"""

    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        """Initializes the Song object"""
        self.source = source
        self.requester = self.source.requester

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


class SongQueue(asyncio.Queue):
    """Class for SongQueue"""

    def __getitem__(self, item) -> Union[Song, list]:
        """Get item from queue"""
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        return self._queue[item]

    def __iter__(self) -> iter:
        """Iterate over queue"""
        return iter(self._queue)

    def __len__(self) -> int:
        """Get length of queue"""
        return self.qsize()

    def clear(self) -> None:
        """Clear queue"""
        self._queue.clear()

    def shuffle(self) -> None:
        """Shuffle queue"""
        random.shuffle(self._queue)

    def remove(self, index: int) -> Song:
        """Remove song from queue"""
        del self._queue[index]
