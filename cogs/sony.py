import io
import json
import requests
import uuid
from bs4 import BeautifulSoup

import discord
from discord.ext import commands, tasks


class Sony(commands.Cog):
    SONY_URL_PREFIX = "https://xperirom.com/devices"

    def __init__(self, bot):
        self.bot = bot
        self.fetch_versions.start()

    def cog_unload(self):
        self.fetch_versions.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @tasks.loop(hours=1)
    async def fetch_versions(self):
        if len(self.bot.guilds) == 0:
            return

        if not hasattr(self, "channel"):
            channel = self.redis.hget("config", "sony.channel")
            if not channel:
                print("Please !config hset config sony.channel #channel")
                return
            channel_id = channel.decode("utf-8")[2:-1]
            print(channel_id)
            self.channel = discord.utils.get(
                self.bot.guilds[0].channels, id=int(channel_id)
            )

        for key, value in self._tracked().items():
            new_version = self._get_version(value["device"], value["customization"])
            print(new_version)

            if not new_version or value["version"] == new_version:
                continue

            value["version"] = new_version
            self.redis.hset("sony-fetch:tracked", key, json.dumps(value))

            embed = discord.Embed(
                title="New version spotted",
                url=f"{self.SONY_URL_PREFIX}/{value['device']}",
            )
            embed.add_field(name="Device", value=value["device"], inline=False)
            embed.add_field(
                name="Customization", value=value["customization"], inline=False
            )
            embed.add_field(name="Version", value=value["version"], inline=False)
            embed.add_field(
                name="URL",
                value=f"{self.SONY_URL_PREFIX}/{value['device']}",
                inline=False,
            )
            await self.channel.send(embed=embed)

    @commands.group()
    @commands.has_role("sony")
    async def sony(self, ctx):
        pass

    @staticmethod
    def _get_version(device, customization):
        content = requests.get(f"{Sony.SONY_URL_PREFIX}/{device}").text
        soup = BeautifulSoup(content, features="html.parser")

        for tr in soup.find("tbody").find_all("tr"):
            td = tr.find_all("td")

            if td[0].text == customization:
                return td[1].text

        return None

    def _tracked(self):
        tracked = {}

        for key, value in self.redis.hscan_iter("sony-fetch:tracked"):
            tracked[key.decode()] = json.loads(value)

        return tracked

    @sony.command()
    @commands.has_role("sony")
    async def track(self, ctx, device, customization):
        self.redis.hset(
            "sony-fetch:tracked",
            str(uuid.uuid4()),
            json.dumps(
                {"device": device, "customization": customization, "version": None}
            ),
        )
        await ctx.message.add_reaction("👍")
        await self.fetch_versions()

    @sony.command()
    @commands.has_role("sony")
    async def untrack(self, ctx, device, customization=None):
        for key, value in self._tracked().items():
            if value["device"] != device:
                continue
            if customization and value["customization"] != customization:
                continue
            self.redis.hdel("sony-fetch:tracked", key)
        await ctx.message.add_reaction("👍")

    @sony.command()
    @commands.has_role("sony")
    async def tracked(self, ctx):
        response = []

        for _, value in self._tracked().items():
            response.append(
                f"{value['url']} {value['device']} {value['customization']}"
            )

        await ctx.reply(
            file=discord.File(
                io.StringIO("\n".join(sorted(response))), filename="tracked.txt"
            )
        )


async def setup(bot):
    await bot.add_cog(Sony(bot))
