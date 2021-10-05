import json
import re

import discord
from discord.ext import commands
import requests


class Gerrit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gerrit_url = "https://review.lineageos.org"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.Cog.listener()
    async def on_message(self, message):
        regex = ".*https://review\.lineageos\.org/(?:(?:#\/)?c\/(?:LineageOS\/[a-zA-Z_0-9\-]*\/\+\/)?)?(\d+).*"
        if match := re.match(regex, message.content):
            req = requests.get(
                f"https://review.lineageos.org/changes/{match[1]}?o=DETAILED_ACCOUNTS"
            )
            change = json.loads(req.text[4:])
            embed = discord.Embed(
                content=f"{self.gerrit_url}/c/{change['_number']}: {change['subject']}",
                title=f"{change['_number']}: {change['subject']} ({change['status']})",
                type="rich",
                url=f"https://review.lineageos.org/c/{change['_number']}",
                colour=discord.Colour.green(),
            )
            embed.set_author(
                name=f'{change["owner"]["name"]} ({change["owner"]["email"]})',
                url=f'{self.gerrit_url}/q/owner:{change["owner"]["username"]}',
            )
            embed.add_field(
                name="Project",
                value=f'[{change["project"]}]({self.gerrit_url}/q/project:{change["project"]})',
            )
            embed.add_field(name="Branch", value=change["branch"])
            if "topic" in change:
                embed.add_field(
                    name="Topic",
                    value=f'[{change["topic"]}]({self.gerrit_url}/q/{change["topic"]})',
                )
            await message.reply(content=None, embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Gerrit(bot))
