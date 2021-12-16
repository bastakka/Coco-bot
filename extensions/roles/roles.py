"""Roles bot commands and listeners cog module"""
import os
import json
import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord import RawReactionActionEvent
from core.basecog import BaseCog


class Roles(BaseCog):
    """Bot Roles commands and listeners class"""

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.reaction_messages_path = self.dir_path + "/reaction_messages.json"
        self.reaction_messages = self._get_reaction_messages()

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

    async def _procces_reaction(self, payload: RawReactionActionEvent, type: str):
        """Procces reaction"""
        payload_id = str(payload.message_id)
        emoji = str(payload.emoji)
        if payload.user_id == self.bot.user.id:
            return

        if payload_id in self.reaction_messages:
            emojies = self.reaction_messages[payload_id]["emojies"]
            if emoji in emojies:

                guild = self.bot.get_guild(payload.guild_id)
                if guild is None:
                    self.logger.warning("Error in fetching guild in procces_reaction")
                    return

                role = guild.get_role(emojies[emoji])
                if role is None:
                    self.logger.warning("Error in fetching role in procces_reaction")
                    return

                user = await guild.fetch_member(payload.user_id)
                if user is None:
                    self.logger.warning("Error in fetching user in procces_reaction")
                    return
                try:
                    if type == "add":
                        return await user.add_roles(role)
                    await user.remove_roles(role)
                except discord.Forbidden:
                    self.logger.warning("Error in proccesing reaction, missing permissions.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self._procces_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self._procces_reaction(payload, "remove")

    async def cog_command_error(self, ctx: ApplicationContext, error: Exception) -> None:
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Could not find channel")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Error. Maybe wrong emoji?")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_add(self, ctx, message: str, emoji: str, role: discord.Role):
        """Add emoji to role"""
        if message not in self.reaction_messages:
            return await ctx.send("Message not found")

        if emoji in self.reaction_messages[message]["emojies"]:
            return await ctx.send("Emoji already exists")

        channel = self.bot.get_channel(
            int(self.reaction_messages[message]["channel_id"])
        )
        if channel is None:
            return await ctx.send("Channel containing this message not found")

        fetched_message = await channel.fetch_message(int(message))
        if fetched_message is None:
            return await ctx.send("Message not found")

        await fetched_message.add_reaction(emoji)
        self.reaction_messages[message]["emojies"][emoji] = role.id
        await ctx.send("Added emoji and role to message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_remove(self, ctx, message: str, emoji: str):
        """Remove emoji from role"""
        if message not in self.reaction_messages:
            return await ctx.send("Message not found")

        if emoji not in self.reaction_messages[message]["emojies"]:
            return await ctx.send("Emoji not found")

        channel = self.bot.get_channel(
            int(self.reaction_messages[message]["channel_id"])
        )
        if channel is None:
            return await ctx.send("Channel containing this message not found")

        fetched_message = await channel.fetch_message(int(message))
        if fetched_message is None:
            return await ctx.send("Message not found")

        await fetched_message.clear_reaction(emoji)
        del self.reaction_messages[message]["emojies"][emoji]
        await ctx.send("Removed emoji and role from message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def emoji_list(self, ctx, message: str):
        """List emojies and roles in message"""
        if message not in self.reaction_messages:
            return await ctx.send("Message not found")

        channel = self.bot.get_channel(
            int(self.reaction_messages[message]["channel_id"])
        )
        if channel is None:
            return await ctx.send("Channel containing this message not found")

        fetched_message = await channel.fetch_message(int(message))
        if fetched_message is None:
            return await ctx.send("Message not found")

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
        embed = discord.Embed(title=title, description=description)
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
        if message not in self.reaction_messages:
            return await ctx.send("Message not found")
        channel = self.bot.get_channel(
            int(self.reaction_messages[message]["channel_id"])
        )
        if channel is None:
            return await ctx.send("Channel containing this message not found")
        fetched_message = await channel.fetch_message(int(message))
        if fetched_message is None:
            return await ctx.send("Message not found")
        await fetched_message.delete()
        del self.reaction_messages[message]
        await ctx.send("Removed message")
        self._save_reaction_messages()

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def message_remove(self, ctx, message: str, *, text: str):
        """Edit message in reaction_messages"""
        if message not in self.reaction_messages:
            return await ctx.send("Message not found")
        channel = self.bot.get_channel(
            int(self.reaction_messages[message]["channel_id"])
        )
        if channel is None:
            return await ctx.send("Channel containing this message not found")
        fetched_message = await channel.fetch_message(int(message))
        if fetched_message is None:
            return await ctx.send("Message not found")
        title = text.split("\n")[0]
        description = "\n".join(text.split("\n")[1:])
        embed = discord.Embed(title=title, description=description)
        await fetched_message.edit(embed=embed)
        await ctx.send("Edited message")
