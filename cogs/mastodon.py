from discord.ext import tasks, commands
from bs4 import BeautifulSoup

import discord
import os
import requests


class Mastodon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('MASTODON_ACCESS_TOKEN', '')}"
        }

    def cog_unload(self):
        self.fetch_mentions.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @tasks.loop(seconds=30)
    async def fetch_mentions(self):
        if len(self.bot.guilds) == 0:
            return

        if not hasattr(self, "channel"):
            channel = self.redis.hget("config", "mastodon.channel")
            if not channel:
                print("Please !config hset config mastodon.channel #channel")
            channel_id = channel.decode("utf-8")[2:-1]
            self.channel = discord.utils.get(
                self.bot.guilds[0].channels, id=int(channel_id)
            )

        last_notif = self.redis.get("mastodon.last_notif")
        if last_notif:
            last_notif = last_notif.decode("utf-8")
        else:
            last_notif = "0"

        url = f"{os.environ.get('MASTODON_BASE_URL')}/api/v1/notifications?exclude_types[]=follow&exclude_types[]=favourite&exclude_types[]=reblog&exclude_types[]=poll&exclude_types[]=follow_request"

        if last_notif:
            url = f"{url}&since_id={last_notif}"

        req = requests.get(url, headers=self.headers, timeout=5)

        if req.status_code == 200:
            for notif in req.json():
                if not last_notif or notif["id"] > last_notif:
                    last_notif = notif["id"]

                soup = BeautifulSoup(notif["status"]["content"], features="html.parser")
                embed = discord.Embed.from_dict(
                    {
                        "title": "New Mention",
                        "type": "rich",
                        "author": {
                            "name": f"{notif['account']['display_name']} ({notif['account']['acct']})",
                            "url": notif["account"]["url"],
                        },
                        "description": soup.get_text(),
                        "thumbnail": {
                            "url": notif["account"]["avatar"],
                        },
                        "url": notif["status"]["url"],
                    }
                )
                await self.channel.send(content=None, embed=embed)
            self.redis.set("mastodon.last_notif", last_notif)
        else:
            print(req.status_code, req.text)


def setup(bot):
    bot.add_cog(Mastodon(bot))
