"""Music bot commands cog module"""
import math
import time

import discord
from discord.ext import commands
from core.basecog import BaseCog

from .songs import Song
from .voicestate import VoiceState
from .ytdlsource import YTDLError, YTDLSource


class Music(BaseCog):
    """Music bot commands cog"""

    def __init__(self, bot) -> None:
        """Music class init with dictionary for voice states"""
        super().__init__(bot)
        self.voice_states = {}

    def _get_voice_state(self, ctx) -> VoiceState:
        """Get the voice state for the current channel"""
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        return state

    def cog_check(self, ctx: commands.Context) -> bool:
        """Check if the user is in a voice channel"""
        if ctx.author.voice is None:
            ctx.send("Stop bothering me, when you are not in a voice channel.")
            return False
        return True

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """Get voice state before command is invoked"""
        author = ctx.author
        message = f"{author.name}#{author.discriminator} issued the command `{ctx.command.name}`"
        chat = ctx.guild.name if ctx.guild else "Direct message"
        log_message = f"{message} in {chat}."
        self.logger.debug(log_message)

        ctx.start = time.time()
        ctx.voice_state = self._get_voice_state(ctx)

    @commands.command(
        name="join", invoke_without_subcommand=True, aliases=["summon", "connect"]
    )
    async def _join(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ) -> None:
        """Summon the bot to a voice channel"""
        if not channel and not ctx.author.voice:
            await ctx.send("Stop bothering me, when you are not in a voice channel.")
            return

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="leave", aliases=["disconnect"])
    async def leave(self, ctx: commands.Context) -> None:
        """Disconnect the bot from the voice channel, clears the queue"""
        if not ctx.voice_state.voice:
            return await ctx.send("Not connected to any voice channel.")
        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        """Plays a song taking query and passing it to youtube_dl"""
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(
                    ctx, query, loop=ctx.voice_state.loop
                )
            except YTDLError as err:
                await ctx.send(
                    f"An error occurred while processing this request: {(str(err))}"
                )
            else:
                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(f"Enqueued {str(source)}")

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the currently playing song and clear the queue"""
        ctx.voice_state.songs.clear()
        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction("⏹")
        else:
            await ctx.send("I am not currently playing anything!")

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context) -> None:
        """Pause the currently playing song"""
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction("⏯")
        else:
            await ctx.send("I am not currently playing anything!")

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context) -> None:
        """Resume the currently paused song"""
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction("⏯")
        else:
            await ctx.send("I am not currently playing anything!")

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context, *, page: int = 1) -> None:
        """Show the player's queue"""
        if not ctx.voice_state.songs:
            return await ctx.send("Empty queue :(")

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)
        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f"`{i + 1}.` [**{song.source.title}**]({song.source.url})\n"

        embed = discord.Embed(
            title=f"Queue for {ctx.guild.name}",
            description=queue,
            color=0xFF0000,
        )
        embed.set_footer(text=f"Page {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(name="remove", aliases=["r"])
    async def remove(self, ctx: commands.Context, index: int) -> None:
        """Removes a song by index"""
        if not ctx.voice_state.songs:
            return await ctx.send("There are no songs in the queue.")

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction("✅")

    @commands.command(name="now", aliases=["current", "playing"])
    async def now(self, ctx: commands.Context) -> None:
        """Display information about the currently playing song"""
        if not ctx.voice_state.voice:
            return await ctx.send("Not connected to any voice channel.")
        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")
        await ctx.send(embed=ctx.voice_state.current.make_song_embed())

    @commands.command(name="skip")
    async def skip(self, ctx: commands.Context) -> None:
        """Skip the currently playing song"""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")
        ctx.voice_state.skip()
        await ctx.message.add_reaction("⏭")

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx: commands.Context, *, volume: int = None) -> None:
        """Change the volume of the player, from 1 to 100"""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")

        if volume is None:
            return await ctx.send(
                f"I am now playing at {ctx.voice_state.volume}% volume."
            )

        if volume < 1 or volume > 200:
            return await ctx.send("Between 1 and 200 please.")

        ctx.voice_state.volume = volume / 100
        await ctx.send(f"Volume set to {volume}%.")

    @commands.command(name="loop")
    async def loop(self, ctx: commands.Context) -> None:
        """Toggle looping the current song"""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction("✅")

    @commands.command(name="shuffle")
    async def shuffle(self, ctx: commands.Context) -> None:
        """Shuffle the queue"""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction("✅")
