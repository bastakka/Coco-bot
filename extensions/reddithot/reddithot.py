"""Reddit bot commands cog module"""
import json
import os
import discord
from discord.ext import commands, tasks
from asyncpraw import Reddit
from asyncprawcore.exceptions import Redirect
from core.basecog import BaseCog


async def _make_reddit_embed(submission):
    """Creates an embed from a reddit submission."""
    await submission.subreddit.load()
    await submission.author.load()
    embed = discord.Embed(
        title=submission.title,
        url="https://reddit.com" + submission.permalink,
        description=submission.selftext,
        color=0xFF0000,
    )
    embed.set_author(
        name=f"r/{submission.subreddit.display_name}",
        icon_url=submission.subreddit.icon_img,
    )
    if not submission.is_self:
        if submission.url.startswith("https://i"):
            embed.set_image(url=submission.url)
        else:
            embed.add_field(
                name="Post is something I do not understand. Check it yourself here:",
                value=submission.url,
            )
    embed.set_footer(
        text=f"From u/{submission.author} | ⬆️ {submission.score} | 💬 {submission.num_comments}",
        icon_url=submission.author.icon_img,
    )
    return embed


class RedditHot(BaseCog):
    """Bot Reddit commands and loop"""

    def __init__(self, bot):
        super().__init__(bot)
        self.subreddit_json_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/subreddits.json"
        )
        self.repost_json_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/reposts.json"
        )
        self.subreddits = self._get_subreddits()
        self.reposts = self._get_reposts()
        self.reddit = Reddit(
            client_id=self.config.reddit["id"],
            client_secret=self.config.reddit["secret"],
            username=self.config.reddit["username"],
            password=self.config.reddit["password"],
            user_agent=self.config.reddit["user_agent"],
        )
        self.reddit.read_only = True

    def _get_subreddits(self):
        """Get subreddits from subreddits local json file"""
        try:
            with open(
                self.subreddit_json_path, "r", encoding="utf-8"
            ) as subreddits_file:
                subreddits = json.load(subreddits_file)
        except FileNotFoundError:
            self.logger.warning(
                "Could not find subreddits.json file, making new one..."
            )
            with open(
                self.subreddit_json_path, "w", encoding="utf-8"
            ) as subreddits_file:
                subreddits = {}
                json.dump(subreddits, subreddits_file, indent=4)
        return subreddits

    def _get_reposts(self):
        """Get repost from repost local json file"""
        try:
            with open(self.repost_json_path, "r", encoding="utf-8") as reposts_file:
                reposts = json.load(reposts_file)
        except FileNotFoundError:
            self.logger.warning("Could not find repost.json file, making new one...")
            with open(self.repost_json_path, "w", encoding="utf-8") as reposts_file:
                reposts = {}
                json.dump(reposts, reposts_file, indent=4)
        return reposts

    def _save_subreddits(self):
        """Save subreddits to local json file"""
        with open(self.subreddit_json_path, "w", encoding="utf-8") as subreddits_file:
            json.dump(self.subreddits, subreddits_file, indent=4)

    def _save_reposts(self):
        """Save repost to repost local json file"""
        with open(self.repost_json_path, "w", encoding="utf-8") as reposts_file:
            json.dump(self.reposts, reposts_file, indent=4)

    def _increment_reposts(self):
        """Increment reposts for subreddit"""
        for repost in self.reposts.copy():
            self.reposts[repost] += 1
            if self.reposts[repost] >= 48:
                self.logger.debug("%s has reached 48 hours, removing from list", repost)
                del self.reposts[repost]

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event"""
        self.reddit_loop.start()  # pylint: disable=no-member

    @tasks.loop(hours=1)
    async def reddit_loop(self):
        """Reddit loop"""
        self.logger.info("Reddit loop started")
        self._increment_reposts()

        for subreddit in self.subreddits:
            self.logger.debug("Fetching %s...", subreddit)
            praw_subreddit = await self.reddit.subreddit(subreddit, fetch=True)
            async for submission in praw_subreddit.hot(limit=6):
                if submission.id not in self.reposts:
                    self.logger.debug("Found new submission: %s", submission.id)
                    self.reposts[submission.id] = 0
                    embed = await _make_reddit_embed(submission)
                    for channel_id in self.subreddits.copy()[subreddit]:
                        try:
                            channel = self.bot.get_channel(channel_id)
                        except discord.NotFound:
                            self.logger.warning(
                                "Could not find channel %s. Deleting...", channel_id
                            )
                            del self.subreddits[subreddit][channel_id]
                            continue
                        await channel.send(embed=embed)

        self._save_reposts()
        self.logger.info("Reddit loop finished")

    @commands.is_owner()
    @commands.command()
    async def subreddit_here(self, ctx, subreddit):
        """Add channel to list of channels to receive hot post form subreddit"""
        try:
            praw_subreddit = await self.reddit.subreddit(subreddit, fetch=True)
        except Redirect:
            return await ctx.send(f"Subreddit {subreddit} not found.")
        subreddit = praw_subreddit.display_name
        if praw_subreddit.over18 and not ctx.channel.is_nsfw():
            return await ctx.send(
                f"Shhhh. Not here. Kids are around. {subreddit} is NSFW."
            )
        if subreddit not in self.subreddits:
            self.subreddits.update({subreddit: []})
        if ctx.channel.id not in self.subreddits[subreddit]:
            self.subreddits[subreddit].append(ctx.channel.id)
            self._save_subreddits()
            return await ctx.send(
                f"{ctx.channel.mention} is now subscribed to {subreddit}"
            )
        return await ctx.send(
            f"{ctx.channel.mention} is already subscribed to {subreddit}"
        )

    @commands.is_owner()
    @commands.command()
    async def subreddit_not_here(self, ctx, subreddit):
        """Remove channel from list of channels to receive hot posts form subreddit"""
        try:
            praw_subreddit = await self.reddit.subreddit(subreddit, fetch=True)
        except Exception as e:
            return await ctx.send(f"Error in finding subreddit {subreddit}\n{e}")
        subreddit = praw_subreddit.display_name
        if ctx.channel.id in self.subreddits[subreddit]:
            self.subreddits[subreddit].remove(ctx.channel.id)
            self._save_subreddits()
            return await ctx.send(
                f"{ctx.channel.mention} is no longer subscribed to {subreddit}"
            )
        return await ctx.send(f"{ctx.channel.mention} is not subscribed to {subreddit}")
