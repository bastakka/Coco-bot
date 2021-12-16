"""Roles bot commands and listeners cog module"""
import sys
import os
import json
from typing import Optional
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
            with open(self.reaction_messages_path, "r", encoding="utf-8") as messages_file:
                return json.load(messages_file)
        except FileNotFoundError:
            self.logger.warning(
                "Could not find reaction_messages.json file, making new one..."
            )
            with open(self.reaction_messages_path, "w", encoding="utf-8") as messages_file:
                messages = {}
                json.dump(messages, messages_file, indent=4)
            return messages

    def _save_reaction_messages(self):
        """Save reaction messages to local json file"""
        with open(self.reaction_messages_path, "w", encoding="utf-8") as messages_file:
            json.dump(self.reaction_messages, messages_file, indent=4)

    async def procces_reaction(self, payload: RawReactionActionEvent, type: Optional[str] = None):


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self.process_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self.process_reaction(payload, "remove")
