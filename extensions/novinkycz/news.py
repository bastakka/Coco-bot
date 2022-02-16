"""Module with News class for news cog"""

from dateutil import parser


class News:
    """News class for parsing news from url"""

    def __init__(self, new, ns) -> None:
        """News class init"""
        self.loc = new.find("loc:loc", ns).text
        news = new.find("news:news", ns)
        self.title = news.find("news:title", ns).text
        temp_date = news.find("news:publication_date", ns).text
        parsed_date = parser.parse(temp_date)
        self.publication_date = parsed_date.strftime("%H:%M %d.%m.%Y")
