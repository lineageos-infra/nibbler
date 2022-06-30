from discord.ext import tasks, commands

import asyncio
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
    async def ou(self, ctx, device=None, update_method="2", incremental_system_version=""):
        if device == None:
            req = requests.get("https://oxygenupdater.com/api/v2.6/devices", headers=self.HEADERS).json()
            if "error" in req:
                await self.reply_and_delete(ctx, f"```\n{json.dumps(req, indent=4)}\n```")
                return
            devices = { x["id"]: x["name"] for x in sorted(req, key=lambda d: int(d["id"])) }
            if ctx.channel.category_id == self.IRC_CATEGORY_ID:
                await self.reply_and_delete(ctx, file=discord.File(io.StringIO(json.dumps(devices, indent=4)), filename="devices.txt"))
            else:
                await self.reply_and_delete(ctx, f"```\n{json.dumps(devices, indent=4)}\n```")
        elif update_method == "?":
            req = requests.get(f"https://oxygenupdater.com/api/v2.6/updateMethods/{device}", headers=self.HEADERS).json()
            if "error" in req:
                await self.reply_and_delete(ctx, f"```\n{json.dumps(req, indent=4)}\n```")
                return
            update_methods = { x["id"]: x["english_name"] for x in sorted(req, key=lambda d: int(d["id"])) }
            if ctx.channel.category_id == self.IRC_CATEGORY_ID:
                await self.reply_and_delete(ctx, file=discord.File(io.StringIO(json.dumps(update_methods, indent=4)), filename="updateMethods.txt"))
            else:
                await self.reply_and_delete(ctx, f"```\n{json.dumps(update_methods, indent=4)}\n```")
        else:
            if len(incremental_system_version) > 0:
                req = requests.get(f"https://oxygenupdater.com/api/v2.6/updateData/{device}/{update_method}/{incremental_system_version}", headers=self.HEADERS).json()
            else:
                req = requests.get(f"https://oxygenupdater.com/api/v2.6/mostRecentUpdateData/{device}/{update_method}", headers=self.HEADERS).json()
            if "error" in req:
                await self.reply_and_delete(ctx, f"```\n{json.dumps(req, indent=4)}\n```")
                return
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
                        "value": req["description"].splitlines()[0].split()[-1],
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
            await self.reply_and_delete(ctx, content=None, embed=embed)

    async def reply_and_delete(self, ctx, *args, **kwargs):
        message = await ctx.reply(*args, **kwargs)
        await asyncio.sleep(60)
        await message.delete()
        await ctx.message.delete()

    def sizeof_fmt(self, num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"


def setup(bot):
    bot.add_cog(OxygenUpdater(bot))
