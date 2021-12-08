from discord.ext import tasks, commands

import discord
import requests


class OxygenUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(hidden=True)
    async def ou(self, ctx, device=None, update_type=2):
        if device == None:
            req = requests.get("https://oxygenupdater.com/api/v2.6/devices").json()
            devices = { x["id"]: x["name"] for x in sorted(req, key=lambda d: int(d["id"])) }
            await ctx.send(f"```{devices}```")
        else:
            req = requests.get(f"https://oxygenupdater.com/api/v2.6/mostRecentUpdateData/{device}/{update_type}").json()
            embed = discord.Embed.from_dict({
                "title": req["ota_version_number"],
                "type": "rich",
                "description": req["changelog"]
                if req["changelog"]
                else "" + "..."
                if len(req["changelog"]) > 140
                else "",
                "url": req["download_url"],
                "color": 15401000,
                "thumbnail": {
                    "url": "https://oxygenupdater.com/img/favicon/android-chrome-192x192.png"
                },
                "fields": [
                    {
                        "name": "MD5",
                        "value": req["md5sum"],
                        "inline": "true"
                    },
                    {
                        "name": "OS version",
                        "value": req["os_version"],
                        "inline": "true"
                    },
                    {
                        "name": "Download size",
                        "value": self.sizeof_fmt(int(req["download_size"])),
                        "inline": "true"
                    },
                    {
                        "name": "Download URL",
                        "value": req["download_url"]
                    }
                ]
            })
            await ctx.send(content=None, embed=embed)

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"


def setup(bot):
    bot.add_cog(OxygenUpdater(bot))
