"""News bot loop and commands cog module"""
import json
import os
import discord
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from core.basecog import BaseCog
from .news import News


async def _get_preview_image_url(url: str) -> str:
    """Get preview image url from news url"""
    respone = requests.get(url)
    if respone.status_code == 200:
        soup = BeautifulSoup(respone.content, "html.parser")
        preview_image_url = soup.find("meta", property="og:image")["content"]
        return preview_image_url


async def _make_new_embed(news) -> discord.Embed:
    """Creates an embed from news"""
    embed = discord.Embed(
        title=news.title,
        url=news.loc,
        color=0xFFFFFF,
    )
    embed.set_author(
        name=f"Novinky.cz",
        icon_url="attachment://logo-novinkycz.png",
    )
    embed.set_footer(text = f"Datum zprávy: {news.publication_date}")
    embed.set_image(url = await _get_preview_image_url(news.loc))
    return embed


class Novinkycz(BaseCog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.news_url = "https://www.novinky.cz/sitemaps/sitemap_news.xml"
        self.ns = {
            "loc": "http://www.sitemaps.org/schemas/sitemap/0.9",
            "news": "http://www.google.com/schemas/sitemap-news/0.9",
        }

        self.news_repost_json_path = self.dir_path + "/news_reposts.json"
        self.news_reposts = self._get_news_reposts()

        self.news_channels_json_path = self.dir_path + "/news_channels.json"
        self.news_channels = self._get_news_channels()

    def _get_news_reposts(self) -> dict:
        """Get news repost from news repost local json file"""
        try:
            with open(
                self.news_repost_json_path, "r", encoding="utf-8"
            ) as news_reposts_file:
                news_reposts = json.load(news_reposts_file)
        except FileNotFoundError:
            self.logger.warning(
                "Could not find news_repost.json file, making new one..."
            )
            with open(
                self.news_repost_json_path, "w", encoding="utf-8"
            ) as news_reposts_file:
                news_reposts = {}
                json.dump(news_reposts, news_reposts_file, indent=4)
        return news_reposts

    def _get_news_channels(self) -> list:
        """Get news channels from news channels local json file"""
        try:
            with open(
                self.news_channels_json_path, "r", encoding="utf-8"
            ) as news_channels_file:
                news_channels = json.load(news_channels_file)
        except FileNotFoundError:
            self.logger.warning(
                "Could not find news_channels.json file, making new one..."
            )
            with open(
                self.news_channels_json_path, "w", encoding="utf-8"
            ) as news_channels_file:
                news_channels = []
                json.dump(news_channels, news_channels_file, indent=4)
        return news_channels

    def _get_news(self) -> dict:
        """Get news from url"""
        self.logger.debug("Fetching news...")
        respone = requests.get(self.news_url)
        news = {}
        if respone.status_code == 200:
            root = ET.fromstring(respone.content)
            for new in root.findall("loc:url", self.ns):
                parsed_new = News(new, self.ns)
                news[parsed_new.loc] = parsed_new
        return news

    def _save_news_reposts(self) -> None:
        """Save repost to repost local json file"""
        with open(self.news_repost_json_path, "w", encoding="utf-8") as reposts_file:
            json.dump(self.news_reposts, reposts_file, indent=4)

    def _save_news_channels(self) -> None:
        """Save news repost to local json file"""
        with open(
            self.news_channels_json_path, "w", encoding="utf-8"
        ) as news_channels_file:
            json.dump(self.news_channels, news_channels_file, indent=4)

    def _increment_news(self) -> None:
        """Increment news"""
        for news_repost in self.news_reposts.copy():
            self.news_reposts[news_repost] += 1
            if self.news_reposts[news_repost] >= 336:
                self.logger.debug(
                    "%s has reached 2 weeks, removing from list", news_repost
                )
                del self.news_reposts[news_repost]

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Bot ready event"""
        self.news_loop.start()  # pylint: disable=no-member

    @tasks.loop(hours=1)
    async def news_loop(self) -> None:
        """News loop"""
        self.logger.info("News loop started")
        self._increment_news()
        news = self._get_news()
        self.logger.debug("News fetched.")
        for new in news:
            if news[new].loc not in self.news_reposts:
                self.logger.debug("Found new news: %s", new.title)
                self.news_reposts[news[new].loc] = 0
                embed = await _make_new_embed(news[new])
                img_author = discord.File(
                    "assets/images/logos/logo-novinkycz.png",
                    filename="logo-novinkycz.png",
                )
                for channel_id in self.news_channels.copy():
                    try:
                        channel = self.bot.get_channel(channel_id)
                    except discord.NotFound:
                        self.logger.warning(
                            "Could not find channel %s. Deleting...", channel_id
                        )
                        del self.news_channels[channel_id]
                        continue
                    await channel.send(file=img_author, embed=embed)
        self._save_news_reposts()
        self.logger.info("News loop finished")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def novinky_here(self, ctx: commands.Context) -> None:
        """Add channel to list of channels to receive news form novinky.cz"""
        if ctx.channel.id not in self.news_channels:
            self.news_channels.append(ctx.channel.id)
            self._save_news_channels()
            return await ctx.send(
                f"{ctx.channel.mention} is now subscribed to novinky.cz"
            )
        return await ctx.send(
            f"{ctx.channel.mention} is already subscribed to novinky.cz"
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def novinky_not_here(self, ctx: commands.Context) -> None:
        """Remove channel from list of channels to receive news form novinky.cz"""
        if ctx.channel.id in self.news_channels:
            self.news_channels.remove(ctx.channel.id)
            self._save_news_channels()
            return await ctx.send(
                f"{ctx.channel.mention} is no longer subscribed to novinky.cz"
            )
        return await ctx.send(f"{ctx.channel.mention} is not subscribed to novinky.cz")
