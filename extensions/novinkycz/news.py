"""Module with News class for news cog"""
import requests
from dateutil import parser
from bs4 import BeautifulSoup


def _get_preview_image_url(url: str) -> str:
    """Get preview image url from news url"""
    respone = requests.get(url)
    if respone.status_code == 200:
        soup = BeautifulSoup(respone.content, "html.parser")
        preview_image_url = soup.find("meta", property="og:image")["content"]
        return preview_image_url


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
        self.preview_image_url = _get_preview_image_url(self.loc)
