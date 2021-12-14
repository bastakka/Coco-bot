"""Module with Definition class for urban cog"""
from datetime import datetime
from dateutil import parser as dateutil_parser


def _parse_decription(description: str) -> str:
    """Parse the description of a definition"""
    description = description.replace("[", "").replace("]", "")
    if len(description) > 1024:
        description = description[:1021] + "..."
    return description


def _parse_example(example: str) -> str:
    """Parse the example of a definition"""
    example = example.replace("[", "").replace("]", "")
    if len(example) > 1024:
        example = example[:1021] + "..."
    return example


def _parse_author(author: str) -> str:
    """Parse the author of a definition"""
    return author.strip()


def _parse_date(date: str) -> datetime:
    """Parse the date of a definition"""
    return dateutil_parser.parse(date)


class Definition:
    """Definition class for urban json parsing"""

    def __init__(self, definition: dict):
        self.definition_dict = definition
        self.term = definition["word"]
        self.url = definition["permalink"]
        self.thumbs_up = definition["thumbs_up"]
        self.thumbs_down = definition["thumbs_down"]
        self.thumbs_balance = self.thumbs_up - self.thumbs_down

    @property
    def description(self) -> str:
        """Definition description property"""
        return _parse_decription(self.definition_dict["definition"])

    @property
    def example(self) -> str:
        """Definition example property"""
        return _parse_example(self.definition_dict["example"])

    @property
    def author(self) -> str:
        """Definition author property"""
        return _parse_author(self.definition_dict["author"]) or "Unknown"

    @property
    def date(self) -> str:
        """Definition date property"""
        return _parse_date(self.definition_dict["written_on"]).strftime("%d, %b %Y")
