"""Module with Definition class for urban cog"""
from datetime import datetime
from dateutil import parser as dateutil_parser

def _parse_decription(description: str) -> str:
    """Parse the description of a definition"""
    description = description.replace('[', '').replace(']', '')
    if len(description) > 1024:
        description = description[:1021] + '...'
    return description


def _parse_example(example: str) -> str:
    """Parse the example of a definition"""
    if example == '':
        return False
    example = example.replace('[', '').replace(']', '')
    if len(example) > 1024:
        example = example[:1021] + '...'
    return example


def _parse_author(author: str) -> str:
    """Parse the author of a definition"""
    author = author.strip()
    if author == '':
        return False
    return author


def _parse_date(date: str) -> datetime:
    """Parse the date of a definition"""
    return dateutil_parser.parse(date)


class Definition:
    """Definition class for urban json parsing"""

    def __init__(self, definition: dict):
        self.term = definition['word']
        self.url = definition['permalink']
        self.description = _parse_decription(definition['definition'])
        self.example = _parse_example(definition['example'])
        self.author = _parse_author(definition['author']) or 'Unknown'
        self.thumbs_up = definition['thumbs_up']
        self.thumbs_down = definition['thumbs_down']
        self.thumbs_balance = self.thumbs_up - self.thumbs_down
        self.date = _parse_date(definition['written_on']).strftime('%d, %b %Y')
