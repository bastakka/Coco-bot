"""Module with Doujin class for nhentai cog"""
from hentai.hentai import Tag
from hentai import Format


def parse_tags(tags: Tag) -> str:
    """Parse tags from a hentai Tag class"""
    return ", ".join(f"{tag.name}" for tag in tags).capitalize() if tags else "None"


def parse_artists(artists: Tag) -> str:
    """Parse artists from a hentai Tag class"""
    return (
        ", ".join(f"{artist.name}" for artist in artists).title()
        if artists
        else "Unspecified"
    )


def parse_languageses(languages: Tag) -> str:
    """Parse languages from a hentai Tag class"""
    return (
        ", ".join(f"{language.name}" for language in languages).title()
        if languages
        else "Unspecified"
    )


def parse_parodies(parodies: Tag) -> str:
    """Parse parodies from a hentai Tag class"""
    return ", ".join(f"{parody.name}" for parody in parodies).title()


class Doujin:
    """Doujin class for Hentai parsing"""

    def __init__(self, hentai_output) -> None:
        """Doujin class init"""
        self.hentai_output = hentai_output
        self.title = hentai_output.title(Format.Pretty)
        self.url = hentai_output.url
        self.image_urls = hentai_output.image_urls
        self.date = hentai_output.upload_date.strftime("%d, %b %Y")

    @property
    def artist(self) -> str:
        """Doujin artist property"""
        return parse_artists(self.hentai_output.artist)

    @property
    def tags(self) -> str:
        """Doujin tags property"""
        return parse_tags(self.hentai_output.tag)

    @property
    def languages(self) -> str:
        """Doujin languages property"""
        return parse_languageses(self.hentai_output.language)

    @property
    def parodies(self) -> str:
        """Doujin parodies property"""
        return (
            parse_parodies(self.hentai_output.parody)
            if self.hentai_output.parody
            else False
        )
