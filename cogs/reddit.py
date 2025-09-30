import os

import discord
import asyncpraw
import textwrap
from discord.ext import tasks, commands


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_posts.start()

    def cog_unload(self):
        self.fetch_posts.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @tasks.loop(seconds=30)
    async def fetch_posts(self):
        if len(self.bot.guilds) == 0:
            return
        if not hasattr(self, "channel"):
            channel = self.redis.hget("config", "reddit.channel")
            if not channel:
                print("Please !config hset config reddit.channel #channel")
                return
            channel_id = channel.decode("utf-8")[2:-1]
            self.channel = discord.utils.get(
                self.bot.guilds[0].channels, id=int(channel_id)
            )
        if not hasattr(self, "done"):
            self.done = [
                x.decode("utf-8") for x in self.redis.lrange("reddit-fetch:done", 0, -1)
            ]
        if not hasattr(self, "_r"):
            self._r = asyncpraw.Reddit(
                user_agent="LineageOS Discord Bot v1.0",
                client_id=os.environ.get("REDDIT_CLIENT_ID"),
                client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
            )
            self._r.read_only = True
            self.subreddit = await self._r.subreddit("lineageos")

        try:
            async for post in self.subreddit.new(limit=10):
                if post.id in self.done:
                    continue
                embed = discord.Embed.from_dict(
                    {
                        "title": textwrap.shorten(f"{post.title} * /r/LineageOS", 256),
                        "type": "rich",
                        "description": post.selftext[:4000]
                        if hasattr(post, "selftext")
                        else "" + "..."
                        if len(post.selftext) > 140
                        else "",
                        "url": f"https://www.reddit.com{post.permalink}",
                        "color": 15158332,
                        "thumbnail": {"url": "https://www.redditstatic.com/icon.png"},
                        "author": {
                            "name": f"/u/{post.author.name}",
                            "url": f"https://reddit.com/u/{post.author.name}",
                        },
                    }
                )
                await self.channel.send(content=None, embed=embed)
                self.redis.lpush("reddit-fetch:done", post.id)
                self.redis.ltrim("reddit-fetch:done", 0, 99)
                self.done = [post.id, *self.done[:99]]
        except Exception as e:
            print(e)

    @commands.group()
    @commands.has_role("Project Director")
    async def reddit(self, ctx):
        pass

    @reddit.command()
    @commands.has_role("Project Director")
    async def flush(self, ctx):
        await ctx.message.delete()
        self.redis.delete("reddit-fetch:done")


async def setup(bot):
    await bot.add_cog(Reddit(bot))
