"""Openai bot commands cog module"""
import os
import random
import time
from collections import deque

import discord
import openai
from discord.ext import commands
from core.basecog import BaseCog


class ChatLog:
    """Chat log class."""

    def __init__(self, author, botname: str):
        """Initialize chat log."""
        self.log = deque(maxlen=50)
        self.author = author
        self.botname = botname
        self.add(f"A conversation between {author.name} and {botname} starts.\n")
        self.add(self.get_random_emotion_log())

    def __str__(self):
        return "".join(message for message in self.log)

    def get_random_emotion_log(self) -> str:
        """Gets random emotion for chat"""
        emotions = [
            "aggresive",
            "angry",
            "annoyed",
            "bored",
            "calm",
            "confused",
            "curious",
            "depressed",
            "disappointed",
            "disgusted",
            "embarrassed",
            "excited",
            "frustrated",
            "happy",
            "hurt",
            "inspired",
            "jealous",
            "lonely",
            "nervous",
            "proud",
            "sad",
            "scared",
            "shocked",
            "stressed",
            "surprised",
            "tired",
            "upset",
            "worried",
        ]
        emotion = random.choice(emotions)
        emotion_log = f"{self.botname} seems really {emotion} today.\n"
        return emotion_log

    def add(self, msg):
        """Add message to log."""
        self.log.append(msg)

    def clear(self):
        """Clear log."""
        self.__init__(self.author, self.botname)


class OpenAI(BaseCog):
    """Bot openai related commands cog"""

    def __init__(self, bot: commands.Bot) -> None:
        """Chat class init with empty chat log for each user.

        Loads an openai API key from config, which it uses to access Completion engine
        """
        super().__init__(bot)
        self.bot = bot
        self.chats = {}
        openai.api_key = self.config.openai["key"]

    def _get_chatlog_from_userid(self, author, botname) -> str:
        """Get chatlog from user id."""
        if author.id not in self.chats:
            self.chats[author.id] = ChatLog(author, botname)
        return str(self.chats[author.id])

    def _get_ai_response(self, author, message: str) -> str:
        """Get AI response from user_id and prompt.

        Response is generator from davinci engine using log bound to user and prompt."""
        botname = self.bot.user.name
        chatlog = self._get_chatlog_from_userid(author, botname)
        prompt = f"{chatlog}\n{author.name}: {message}\n{botname}: "
        response = openai.Completion.create(
            prompt=prompt,
            engine="davinci",
            stop=[f"\n{author.name}", f"\n{botname}"],
            temperature=0.8,
            top_p=1,
            frequency_penalty=0.7,
            best_of=1,
            max_tokens=150,
        )
        answer = response.choices[0].text.strip()
        self.chats[author.id].add(f"\n{author.name}: {message}\n{botname}: {answer}")
        if answer == "":
            answer = "*silence*"
        return answer

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """Chat in Direct message by default.

        If the message is a command, it will be ignored.
        """
        if message.author.bot:
            return

        if message.content.lower().startswith(
            "coco "
        ):  # Ignore commands in Direct message
            return  # Which is always "coco " from bot.py

        if message.guild is None:
            text_channel = message.channel
            async with text_channel.typing():
                log_channel = self.bot.get_channel(int(self.config.bot_log_channel_id))
                log_user = f"{message.author.name}#{message.author.discriminator}"
                log_message = log_user + " issued `openai` in Direct message."
                await log_channel.send(log_message)
                self.logger.info(log_message)
                start = time.time()

                content = message.content
                author = message.author
                answer = self._get_ai_response(author, content)
                await message.author.send(answer)

                end = time.time()
                delta = end - start
                log_message = "Openai response took: "
                log_message += f" {format(delta, '.2f')} seconds."
                self.logger.info(log_message)
            await log_channel.send(log_message)

    @commands.command()
    async def chat(self, ctx: commands.Context, *, message: str):
        """Bot chat command taking message as an argument.

        Adds message to chat log if there is any and passes entire log to Completion engine.
        First response from Completion engine is taken as an ouput and sent to user.

        Log is generated by separating output of the user and the Completion engine.
        Log is then saved as a deque list of maximum len of 20
        """
        async with ctx.typing():
            author = ctx.author
            answer = self._get_ai_response(author, message)
        await ctx.send(answer)

    @commands.command()
    async def log(self, ctx: commands.Context):
        """Bot command that shows user's openai chat log.

        Chat log is sent to user as a string
        """
        chatlog = self._get_chatlog_from_userid(ctx.author, self.bot.user.name).strip()
        if len(chatlog) > 2000:
            await ctx.send("Chat log is too long to be sent to user.")
            with open("chatlog.tmp", "w", encoding="utf-8") as temp_file:
                temp_file.write(chatlog)
                await ctx.send(file=discord.File("chatlog.tmp"))
            return
        chatlog = f"```{chatlog}```"
        await ctx.send(chatlog)
        os.remove("chatlog.tmp")

    @commands.command()
    async def log_clear(self, ctx: commands.Context):
        """Bot command that clears user's openai chat log.

        Chat log is reinitialized as a new deque list of maximum len of 20
        """
        self.chats[ctx.author.id].clear()
        await ctx.send("Chat log cleared.")


def setup(bot) -> None:
    """Setup function used by discord.py extension loader.

    Adds Chat cog to bot.
    """
    bot.add_cog(OpenAI(bot))
