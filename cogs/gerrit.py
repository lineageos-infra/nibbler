import json
import re
import textwrap

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
        regex = r"https://review\.lineageos\.org/(?:(?:#\/)?c\/(?:LineageOS\/[a-zA-Z_0-9\-]*\/\+\/)?)?(\d+)"
        matches = set(re.findall(regex, re.sub("<.*?>", "", message.content)))
        if len(matches) > 3:
            return
        for match in matches:
            req = requests.get(
                f"https://review.lineageos.org/changes/{match}?o=DETAILED_ACCOUNTS&o=DETAILED_ACCOUNTS&o=CURRENT_REVISION&o=CURRENT_COMMIT"
            )
            change = json.loads(req.text[4:])
            commit = change["revisions"][change["current_revision"]]["commit"]
            embed = discord.Embed(
                title=textwrap.shorten(
                    f"{change['_number']}: {change['subject']} ({change['status']})",
                    256,
                ),
                description=commit["message"].split("\n", 1)[-1].strip(),
                type="rich",
                url=f"https://review.lineageos.org/c/{change['_number']}",
                colour=discord.Colour.green(),
            )
            name = change["owner"]["name"]
            if "email" in change["owner"]:
                name += f" ({change['owner']['email']})"
            embed.set_author(
                name=name,
                url=f"{self.gerrit_url}/q/owner:{change['owner']['username']}",
            )
            embed.add_field(
                name="Project",
                value=f"[{change['project']}]({self.gerrit_url}/q/project:{change['project']})",
            )
            embed.add_field(name="Branch", value=change["branch"])
            if "topic" in change:
                embed.add_field(
                    name="Topic",
                    value=f"[{change['topic']}]({self.gerrit_url}/q/{change['topic']})",
                )
            await message.reply(content=None, embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(Gerrit(bot))
