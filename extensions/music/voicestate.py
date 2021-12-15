"""Voice state class for music module"""
import asyncio
import discord

from async_timeout import timeout
from discord.ext import commands

from extensions.music.ytdlsource import YTDLError
from .song import Song
from .songqueue import SongQueue
from .ytdlsource import YTDLSource

class VoiceError(Exception):
    """Exception for voice related errors"""

class VoiceState:
    """Bot voice state for each guild"""

    def __init__(self, bot: commands.Bot, ctx: commands.Context) -> None:
        """Init voice state"""
        self.bot = bot
        self.ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self.loop = False
        self._volume = 0.5
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    @property
    def volume(self) -> float:
        """Get volume"""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        """Set volume"""
        self._volume = value
        if self.voice:
            self.current.source.volume = value

    def __del__(self) -> None:
        self.audio_player.cancel()
    
    def is_playing(self) -> bool:
        """Check if player is playing"""
        try:
            return self.voice.is_playing()
        except:
            return False
    
    def is_paused(self) -> bool:
        """Check if player is paused"""
        return self.voice.is_paused()
    
    def skip(self) -> None:
        """Skip song"""
        if self.voice:
            self.voice.stop()

    def shuffle(self) -> None:
        """Shuffle queue"""
        self.songs.shuffle()
    
    def pause(self) -> None:
        """Pause voice"""
        self.voice.pause()

    def resume(self) -> None:
        """Resume voice"""
        self.voice.resume()

    async def connect(self, destination: discord.VoiceChannel) -> None:
        """Connect to voice channel"""
        self.voice = await destination.connect()

    async def move_to(self, destination: discord.VoiceChannel) -> None:
        """Move to voice channel"""
        await self.voice.move_to(destination)
    
    async def stop(self) -> None:
        """Stop voice"""
        self.songs.clear()
        if self.voice:
            await self.voice.disconnect()
            self.voice = None
        
    async def add_song(self, query: str) -> Song:
        """Add song to queue"""
        try:
            source = await YTDLSource.create_source(self.ctx, query)
            song = Song(source)
        except YTDLError as err:
            raise VoiceError(str(err))
        await self.songs.put(song)
        return song

    async def redo_song(self) -> Song:
        """Redo song"""
        source = await YTDLSource.create_source(self.ctx, self.current.source.url)
        try:
            song = Song(source)
        except YTDLError as err:
            raise VoiceError(str(err))
        return song

    async def audio_player_task(self) -> None:
        """Audio player task"""
        while True:
            self.next.clear()

            if self.loop:
                song = await self.redo_song()
                self.current.source = song.source
            else:
                try:
                    async with timeout(180):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return
            
            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send("Now playing:", embed=self.current.make_song_embed())
            await self.next.wait()


    def play_next_song(self, error: Exception = None) -> None:
        """Play next song"""
        if error:
            raise VoiceError(str(error))
        self.next.set()