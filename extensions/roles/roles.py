"""Roles bot commands and listeners cog module"""
import os
import json
from typing import Optional
import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands, tasks
from discord import RawReactionActionEvent
from core.basecog import BaseCog


class MessageNotFound(Exception):
    """Raised when a message is not found"""


class ChannelNotFound(Exception):
    """Raised when a channel is not found"""


class EmojiAlreadyExists(Exception):
    """Raised when an emoji already exists"""


class EmojiNotInMessage(Exception):
    """Raised when an emoji is not in a reaction message"""


class Roles(BaseCog):
    """Bot Roles commands and listeners class"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.reaction_messages_path = self.dir_path + "/reaction_messages.json"
        self.reaction_messages = self._get_reaction_messages()

    async def _message_in_messages(self, message: str) -> bool:
        """Check if message is in reaction messages"""
        return message in self.reaction_messages

    async def _emoji_in_message(self, message: str, emoji: str) -> bool:
        """Check if emoji is in message"""
        return emoji in self.reaction_messages[message]["emojies"]

    async def _fetch_message(
        self, channel: discord.TextChannel, message_id: int
    ) -> Optional[discord.Message]:
        """Fetch message from channel by id"""
        try:
            return await channel.fetch_message(message_id)
        except discord.NotFound as err:
            raise MessageNotFound from err

    async def _get_channel_by_id(self, channel_id: int) -> discord.TextChannel:
        """Get channel by id"""
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            raise ChannelNotFound
        return channel

    async def _get_guild_by_id(self, guild_id: int) -> discord.Guild:
        """Get guild by id"""
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            raise discord.NotFound
        return guild

    async def _get_role_by_id(self, guild: discord.Guild, role_id: int) -> discord.Role:
        """Get role from guild by id"""
        role = guild.get_role(role_id)
        if role is None:
            raise discord.NotFound
        return role

    async def _get_user_by_id(self, guild: discord.Guild, user_id: int) -> discord.User:
        """Get user from guild by id"""
        user = guild.get_member(user_id)
        if user is None:
            raise discord.NotFound
        return user

    async def _procces_reaction(self, payload: RawReactionActionEvent, type: str):
        """Procces reaction"""
        payload_id = str(payload.message_id)
        emoji = str(payload.emoji)
        if payload.user_id == self.bot.user.id:
            return

        if payload_id in self.reaction_messages:
            emojies = self.reaction_messages[payload_id]["emojies"]
            if emoji in emojies:

                guild = self._get_guild_by_id(payload.guild_id)
                role = self._get_role_by_id(guild, emojies[emoji])
                user = self._get_user_by_id(guild, payload.user_id)

                try:
                    if type == "add":
                        return await user.add_roles(role)
                    await user.remove_roles(role)
                except discord.Forbidden:
                    self.logger.warning(
                        "Error in proccesing reaction, missing permissions."
                    )

    def _get_reaction_messages(self):
        """Get reaction messages from reaction messages local json file"""
        try:
            with open(
                self.reaction_messages_path, "r", encoding="utf-8"
            ) as messages_file:
                return json.load(messages_file)
        except FileNotFoundError:
            self.logger.warning(
                "Could not find reaction_messages.json file, making new one..."
            )
            with open(
                self.reaction_messages_path, "w", encoding="utf-8"
            ) as messages_file:
                messages = {}
                json.dump(messages, messages_file, indent=4)
            return messages

    def _save_reaction_messages(self):
        """Save reaction messages to local json file"""
        with open(self.reaction_messages_path, "w", encoding="utf-8") as messages_file:
            json.dump(self.reaction_messages, messages_file, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self._procces_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self._procces_reaction(payload, "remove")

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event"""
        self.check_messages.start()  # pylint: disable=no-member

    async def cog_command_error(
        self, ctx: ApplicationContext, error: Exception
    ) -> None:
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Could not find channel")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"Error. I still don't know how to describe which.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_add(self, ctx, message: str, emoji: str, role: discord.Role):
        """Add emoji to role"""
        if not await self._message_in_messages(message):
            raise MessageNotFound
        if await self._emoji_in_message(message, emoji):
            raise EmojiAlreadyExists
        channel = await self._get_channel_by_id(
            self.reaction_messages[message]["channel_id"]
        )
        fetched_message = await self._fetch_message(channel, int(message))

        await fetched_message.add_reaction(emoji)
        self.reaction_messages[message]["emojies"][emoji] = role.id
        await ctx.send("Added emoji and role to message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_remove(self, ctx, message: str, emoji: str):
        """Remove emoji from role"""
        if not await self._message_in_messages(message):
            raise MessageNotFound
        if not await self._emoji_in_message(message, emoji):
            raise EmojiNotInMessage
        channel = await self._get_channel_by_id(
            self.reaction_messages[message]["channel_id"]
        )
        fetched_message = await self._fetch_message(channel, int(message))

        await fetched_message.clear_reaction(emoji)
        del self.reaction_messages[message]["emojies"][emoji]
        await ctx.send("Removed emoji and role from message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_list(self, ctx, message: str):
        """List emojies and roles in message"""
        if not await self._message_in_messages(message):
            raise MessageNotFound

        emojies = self.reaction_messages[message]["emojies"]
        if len(emojies) == 0:
            return await ctx.send("No emojies found")

        await ctx.send(
            "Emojies and roles in message:\n"
            + "\n".join(
                [
                    f"{emoji} - {self.bot.get_guild(ctx.guild.id).get_role(emojies[emoji])}"
                    for emoji in emojies
                ]
            )
        )

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def message_add(self, ctx, channel: discord.TextChannel, *, text: str):
        """Create message in channel with text and add message to reaction_messages"""
        if channel is None:
            return await ctx.send("Channel not found")
        if text == "":
            return await ctx.send("Message cannot be empty")
        title = text.split("\n")[0]
        description = "\n".join(text.split("\n")[1:])
        embed = discord.Embed(
            title="" if title.strip() == "empty" else title,
            description=description,
            color=int(self.config.color)
        )
        message = await channel.send(embed=embed)

        self.reaction_messages[str(message.id)] = {
            "channel_id": channel.id,
            "emojies": {},
        }
        self._save_reaction_messages()
        await ctx.send(f"Made new reaction message with ID: {message.id}")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def message_remove(self, ctx, message: str):
        """Remove message from reaction_messages"""
        if not await self._message_in_messages(message):
            raise MessageNotFound
        channel = await self._get_channel_by_id(
            self.reaction_messages[message]["channel_id"]
        )
        fetched_message = await self._fetch_message(channel, int(message))

        await fetched_message.delete()
        del self.reaction_messages[message]
        await ctx.send("Removed message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def message_edit(self, ctx, message: str, *, text: str):
        """Edit message in reaction_messages"""
        if not await self._message_in_messages(message):
            raise MessageNotFound
        channel = await self._get_channel_by_id(
            self.reaction_messages[message]["channel_id"]
        )
        fetched_message = await self._fetch_message(channel, int(message))

        title = text.split("\n")[0]
        description = "\n".join(text.split("\n")[1:])
        embed = discord.Embed(
            title="" if title.strip() == "empty" else title,
            description=description,
            color=int(self.config.color)
        )
        await fetched_message.edit(embed=embed)
        await ctx.send("Edited message")

    @tasks.loop(hours=24)
    async def check_messages(self):
        self.logger.info("Roles loop started")
        for message in self.reaction_messages.copy():
            try:
                channel = await self._get_channel_by_id(
                    self.reaction_messages[message]["channel_id"]
                )
            except ChannelNotFound:
                self.logger.warning(
                    f"Channel not found for message {message}, removing message."
                )
                del self.reaction_messages[message]
                continue
            try:
                fetched_message = await self._fetch_message(channel, int(message))
            except MessageNotFound:
                self.logger.warning(f"Message {message} not found, removing message.")
                del self.reaction_messages[message]
                continue
            for emoji in self.reaction_messages[message]["emojies"]:
                if not await self._emoji_in_message(message, emoji):
                    await fetched_message.remove_reaction(emoji, self.bot.user)
        self._save_reaction_messages()
        self.logger.info("Roles loop finished")
