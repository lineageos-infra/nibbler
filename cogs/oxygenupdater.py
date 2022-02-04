from discord.ext import tasks, commands

import discord
import io
import json
import requests


class OxygenUpdater(commands.Cog):
    HEADERS = {
        "User-Agent": "Oxygen_updater_5.5.0",
    }
    IRC_CATEGORY_ID = 628008281121751070

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(hidden=True)
    async def ou(self, ctx, device=None, update_method="2"):
        if device == None:
            req = requests.get("https://oxygenupdater.com/api/v2.6/devices", headers=self.HEADERS).json()
            if "error" in req:
                await ctx.reply(f"```\n{json.dumps(req, indent=4)}\n```")
                return
            devices = { x["id"]: x["name"] for x in sorted(req, key=lambda d: int(d["id"])) }
            if ctx.channel.category_id == self.IRC_CATEGORY_ID:
                await ctx.reply(file=discord.File(io.StringIO(json.dumps(devices, indent=4)), filename="devices.txt"))
            else:
                await ctx.reply(f"```\n{json.dumps(devices, indent=4)}\n```")
        elif update_method == "?":
            req = requests.get(f"https://oxygenupdater.com/api/v2.6/updateMethods/{device}", headers=self.HEADERS).json()
            if "error" in req:
                await ctx.reply(f"```\n{json.dumps(req, indent=4)}\n```")
                return
            update_methods = { x["id"]: x["english_name"] for x in sorted(req, key=lambda d: int(d["id"])) }
            if ctx.channel.category_id == self.IRC_CATEGORY_ID:
                await ctx.reply(file=discord.File(io.StringIO(json.dumps(update_methods, indent=4)), filename="updateMethods.txt"))
            else:
                await ctx.reply(f"```\n{json.dumps(update_methods, indent=4)}\n```")
        else:
            req = requests.get(f"https://oxygenupdater.com/api/v2.6/mostRecentUpdateData/{device}/{update_method}", headers=self.HEADERS).json()
            if "error" in req:
                await ctx.reply(f"```\n{json.dumps(req, indent=4)}\n```")
                return
            os_version = req["description"].splitlines()[0].split()[-1]
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
                        "value": os_version,
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
            await ctx.reply(content=None, embed=embed)

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"


def setup(bot):
    bot.add_cog(OxygenUpdater(bot))
