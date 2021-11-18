import discord
import requests

from discord.ext import tasks, commands

class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitor_loop.start()


    def cog_unload(self):
        self.monitor_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @tasks.loop(seconds=15)
    async def monitor_loop(self):
        if len(self.bot.guilds) == 0:
            return
        if not hasattr(self, "channel"):
            self.channel = discord.utils.get(self.bot.guilds[0].channels, name="infra-alerts")
        '''Do some basic monitoring on infra things
        '''
        try:

            msg = ""
            status_codes = {
                "https://stats.lineageos.org/metrics": 200,
                "https://download.lineageos.org/metrics": 200
            }
            for site, code in status_codes.items():
                response = requests.get(site)
                if response.status_code != code:
                    msg += f"{site}: expected {code}, got {response.code}"

            gerrit = requests.get("https://review.lineageos.org/config/server/healthcheck~status")
            if gerrit.status_code != 200:
                msg += "problem with gerrit"
                msg += "```"
                msg += gerrit.text[5:]
                msg += "```"

            expected_wiki_version = "expected version not found"
            ghwiki = requests.get("https://api.github.com/repos/LineageOS/lineage_wiki/branches/master")
            if ghwiki.status_code == 200:
                data = ghwiki.json()
                expected_wiki_version = data.get("commit", {}).get("sha", "unexpected github response")

            actual_wiki_version = "actual version not found"
            wiki = requests.get("https://wiki.lineageos.org/version.json")
            if wiki.status_code == 200:
                data = wiki.json()
                actual_wiki_version = data.get("git")
            if not expected_wiki_version.startswith(actual_wiki_version):
                msg += f'Expected wiki version "{expected_wiki_version}", deployed wiki version "{actual_wiki_version}"'

            if msg:
                await self.channel.send(content=msg)
        except:
            pass

def setup(bot):
    bot.add_cog(Monitor(bot))
