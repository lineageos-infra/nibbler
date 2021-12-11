from discord.ext import commands
import requests


class Garbage(commands.Cog):
    MACROS = {
        "acronym": "Lineage, or lineage. Not LOS or LAOS or LAOD.",
        "ask": "Yes - you can ask questions here - you just did! Please get to the point, we don't have all day.",
        "bugs": "https://wiki.lineageos.org/bugreport-howto.html",
        "devices": "Supported devices list: https://wiki.lineageos.org/devices/. Requests for additions can be made at https://undocumented.software/device_request/",
        "eta": "Please don't ask for ETAs. We don't provide them.",
        "how": "Stop asking questions you'll go blind.",
        "logcat": "Logcat: https://i.imgur.com/bSwnH7B.jpg. Follow this: https://wiki.lineageos.org/logcat.html and paste it to https://vomitb.in",
        "muricana": "https://tenor.com/view/american-eagle-usa-usa-flag-gif-14222446",
        "next": "Another satisfied customer. NEXT!",
        "shipit": "https://memegenerator.net/img/instances/54219302/lgtm-ship-it.jpg",
        "watcannon": "https://64.media.tumblr.com/d655daf4856de7e1a45d4a180ad3d5ea/tumblr_muv69e0RvZ1shlw0so1_500.gif",
        "what": "https://tenor.com/view/goat-scary-animal-crazy-animal-scary-goat-wtf-gif-5548755",
        "why": "Because, that's why.",
        "yw": "You're welcome",
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(hidden=True, name=list(MACROS.keys())[0], aliases=list(MACROS.keys())[1:])
    async def _macro(self, ctx):
        await ctx.send(self.MACROS[ctx.invoked_with])

    @commands.command(hidden=True)
    async def catfact(self, ctx):
        req = requests.get("https://itvends.com/catfacts.php?format=text")
        await ctx.send(req.text)

    @commands.command(hidden=True)
    async def vend(self, ctx):
        req = requests.get("https://itvends.com/vend.php?format=text")
        await ctx.send(f"_vends {req.text}_")


def setup(bot):
    bot.add_cog(Garbage(bot))
