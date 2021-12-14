"""Module with Voicestate class for music cog"""
import asyncio
import discord

from async_timeout import timeout
from discord.ext import commands

from .songs import SongQueue
from .ytdlsource import YTDLSource


class VoiceError(Exception):
    """Exception for voice related errors"""


class VoiceState:
    """State of voice channel"""

    def __init__(self, bot: commands.Bot, ctx: commands.Context) -> None:
        self.bot = bot
        self.ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def __del__(self) -> None:
        self.audio_player.cancel()

    @property
    def is_playing(self) -> bool:
        """Check if player is playing"""
        return self.voice and self.current

    async def audio_player_task(self) -> None:
        """Audio player task"""
        while True:
            self.next.clear()

            if self.loop:
                source_audio = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS
                )
                self.current.source = discord.PCMVolumeTransformer(
                    source_audio, self._volume
                )
            else:
                try:
                    async with timeout(180):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self.volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.make_song_embed())
            await self.next.wait()

    def play_next_song(self, error: Exception = None) -> None:
        """Play next song"""
        if error:
            raise VoiceError(str(error))
        self.next.set()

    def skip(self) -> None:
        """Skip song"""
        if self.is_playing:
            self.voice.stop()

    async def stop(self) -> None:
        """Stop voice"""
        self.songs.clear()
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

    @property
    def volume(self) -> float:
        """Get volume"""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        """Set volume"""
        self._volume = value
        if self.is_playing:
            self.current.source.volume = value

    @property
    def loop(self) -> bool:
        """Check if loop is enabled"""
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        """Set loop"""
        self._loop = value
