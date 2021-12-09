"""Module with Chatlog class for openai-chat."""
from collections import deque
import random

class ChatLog:
    """Chat log between aurhor and bot class."""

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
