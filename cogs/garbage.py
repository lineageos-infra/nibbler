from datetime import datetime, timedelta
from discord.ext import commands
import random
import requests


class Garbage(commands.Cog):
    MACROS = {
        "acronym": "Lineage, or lineage. Not LOS or LAOS or LAOD.",
        "ask": "Yes - you can ask questions here - you just did! Please get to the point, we don't have all day.",
        "bugs": "https://wiki.lineageos.org/bugreport-howto.html",
        "devices": "Supported devices list: https://wiki.lineageos.org/devices/. Requests for additions can be made at https://undocumented.software/device_request/",
        "eta": "Please don't ask for ETAs. We don't provide them.",
        "gapps": "https://wiki.lineageos.org/gapps.html",
        "how": "Stop asking questions you'll go blind.",
        "logcat": "Logcat: https://i.imgur.com/bSwnH7B.jpg. Follow this: https://wiki.lineageos.org/logcat.html and paste it to https://vomitb.in",
        "steppum"[::-1]: "5289ddfaa0532477f5c920dc85dec162/bmobkruof/moc.buhtig.tsig//:sptth"[::-1],
        "muricana": "https://tenor.com/view/american-eagle-usa-usa-flag-gif-14222446",
        "next": "Another satisfied customer. NEXT!",
        "nibble": "_OM NOM NOM_",
        "roll": lambda: f"The answer is: {random.choices(['yes', 'no', 'maybe'], weights=[0.05, 0.65, 0.30])[0]}",
        "shipit": "https://memegenerator.net/img/instances/54219302/lgtm-ship-it.jpg",
        "unofficial": "This channel is for help with official roms obtained from https://download.lineageos.org/. Unofficial roms are not made by LineageOS, thus can be very different. Please seek support for unofficial roms from where you got it.",
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
        value = self.MACROS[ctx.invoked_with]
        await ctx.send(value() if callable(value) else value)

    @commands.command(hidden=True)
    async def catfact(self, ctx):
        req = requests.get("https://itvends.com/catfacts.php?format=text")
        await ctx.send(req.text)

    @commands.command(hidden=True)
    async def vend(self, ctx):
        req = requests.get("https://itvends.com/vend.php?format=text")
        await ctx.send(f"_vends {req.text}_")

    @commands.command(hidden=True)
    async def goat(self, ctx):
        req = requests.get("https://goats.fly.dev/")
        await ctx.send(f"zifnab is going to become a goat farmer because {req.text}")

    @commands.command(hidden=True)
    async def when(self, ctx, *devices):
        reply = []

        for device in devices:
            try:
                random.seed(device, version=1)
            except:
                random.seed(device)

            dw = int(random.random() * 7) + 1

            date = datetime.today()
            while dw != date.isoweekday():
                date += timedelta(days=1)

            reply.append(str((device, date.strftime("%A, %Y-%m-%d"))))

        if reply := '\n'.join(reply):
            await ctx.reply(reply)

    @commands.command(hidden=True)
    async def wiki(self, ctx, device):
        req = requests.get("https://raw.githubusercontent.com/LineageOS/hudson/master/updater/devices.json")
        devices = set(e['model'] for e in req.json())

        if device in devices:
            await ctx.send(f"Info: https://wiki.lineageos.org/devices/{device}")
        else:
            await ctx.send(f"Maybe you could support {device} yourself?")


def setup(bot):
    bot.add_cog(Garbage(bot))
