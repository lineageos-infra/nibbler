import json
import os
import re
import time

import discord
from discord.ext import commands
import requests


class Cve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.Cog.listener()
    async def on_message(self, message):
        regex = ".*(CVE-\d{4}-\d{4,7}).*"
        if match := re.match(regex, message.content):
            r = requests.get("https://cve.circl.lu/api/cve/{}".format(match[1]))
            if r.status_code == 200:
                summary = r.json()["summary"]
                url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(
                    match[1]
                )
                embed = discord.Embed(
                    description=summary,
                    title=match[1],
                    type="rich",
                    colour=discord.Colour.red(),
                    url=url,
                )
                await message.reply(content=None, embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Cve(bot))
