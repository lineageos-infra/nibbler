import random
from datetime import datetime, timedelta

import requests
from discord.ext import commands


class Garbage(commands.Cog):
    IRC_CATEGORY_ID = 628008281121751070
    MACROS = {
        'acronym': 'Lineage, or lineage. Not LOS or LAOS or LAOD.',
        'ask': "Yes - you can ask questions here - you just did! Please get to the point, we don't have all day.",
        'bridge': "Discord is bridged with #lineageos IRC channels over at https://libera.chat, feel free to read the FAQ over there if you don't know what IRC is.",
        'bug': 'https://wiki.lineageos.org/bugreport-howto.html',
        'bugs': 'https://wiki.lineageos.org/bugreport-howto.html',
        'devices': 'Supported devices list: https://wiki.lineageos.org/devices/. Requests for additions can be made at https://undocumented.software/device_request/',
        'eta': "Please don't ask for ETAs. We don't provide them.",
        'faq': 'See the FAQ here: https://wiki.lineageos.org/faq.html',
        'frp': 'https://gist.github.com/luk1337/fa47c87daa06b6bf7dfa24dde1e39350',
        'gapps': 'https://wiki.lineageos.org/gapps.html',
        'how': "Stop asking questions you'll go blind.",
        'ims': 'https://wiki.lineageos.org/quirks/ims/',
        'lfs': 'https://gist.github.com/luk1337/a40bb0dbb09bf52e0f50a6f525fb858f',
        'logcat': 'Logcat: https://i.imgur.com/bSwnH7B.jpg. Follow this: https://wiki.lineageos.org/logcat.html and paste it to https://vomitb.in',
        'steppum'[::-1]: 'steppum/oi.buhtig.7331kul//:sptth'[::-1],
        'muricana': 'https://tenor.com/view/american-eagle-usa-usa-flag-gif-14222446',
        'next': 'Another satisfied customer. NEXT!',
        'nibble': '_OM NOM NOM_',
        'nightly': 'LineageOS is built on a !weekly basis. The nightly version string is historical.',
        'roll': lambda: f'The answer is: {random.choices(["yes", "no", "maybe"], weights=[0.05, 0.65, 0.30])[0]}',
        'snet': 'https://wiki.lineageos.org/quirks/snet/',
        'shipit': 'https://memegenerator.net/img/instances/54219302/lgtm-ship-it.jpg',
        'stable': 'A stable is where horses are kept. Lineage automatic builds are done on a !weekly basis',
        'unofficial': 'This channel is for help with official roms obtained from https://download.lineageos.org/. Unofficial roms are not made by LineageOS, thus can be very different. Please seek support for unofficial roms from where you got it.',
        'watcannon': 'https://64.media.tumblr.com/d655daf4856de7e1a45d4a180ad3d5ea/tumblr_muv69e0RvZ1shlw0so1_500.gif',
        'weekly': 'LineageOS is built on a weekly basis (not nightly). The nightly version string is historical. <https://github.com/LineageOS/hudson/blob/main/lineage-build-targets>',
        'what': 'https://tenor.com/view/goat-scary-animal-crazy-animal-scary-goat-wtf-gif-5548755',
        'why': "Because, that's why.",
        'wiki': 'Please consult the Wiki, it is a wealth of useful information. https://wiki.lineageos.org Please note: reading comprehension skills ARE required!',
        'winadb': 'https://gist.github.com/luk1337/1f0d99892e25d9788e6d369905807e9f',
        'winusb': 'https://gist.github.com/luk1337/4bfab1d19ee472307f9077fba872d037',
        'yw': "You're welcome",
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @commands.command(
        hidden=True,
        name=list(MACROS.keys())[0],
        aliases=list(MACROS.keys())[1:],
    )
    async def _macro(self, ctx):
        value = self.MACROS[ctx.invoked_with]
        await ctx.send(value() if callable(value) else value)

    @commands.command(hidden=True)
    async def catfact(self, ctx):
        req = requests.get(
            'https://raw.githubusercontent.com/itvends/web/master/itvends.com/catfacts.txt'
        )
        await ctx.send(random.choice(req.text.splitlines()))

    @commands.command(hidden=True)
    async def dogfact(self, ctx):
        req = requests.get(
            'https://raw.githubusercontent.com/itvends/web/master/itvends.com/catfacts.txt'
        )
        facts = (
            req.text.replace('cat', 'dog')
            .replace('Cat', 'Dog')
            .replace('kittens', 'puppies')
            .replace('kitten', 'puppy')
            .splitlines()
        )
        await ctx.send(random.choice(facts))

    @commands.command(hidden=True)
    async def vend(self, ctx):
        req = requests.get('https://itvends.com/vend.php?format=text')
        await ctx.send(f'_vends {req.text}_')

    @commands.command(hidden=True)
    async def goat(self, ctx):
        req = requests.get('https://goats.fly.dev/')
        await ctx.send(
            f'zifnab is going to become a goat farmer because {req.text}'
        )

    @commands.command(hidden=True)
    async def when(self, ctx, *devices):
        reply = []

        if ctx.channel.category_id == self.IRC_CATEGORY_ID:
            devices = devices[:1]

        for device in devices:
            dw = random.Random(device).randint(1, 7)

            date = datetime.today()
            while dw != date.isoweekday():
                date += timedelta(days=1)

            reply.append(str((device, date.strftime('%A, %Y-%m-%d'))))

        if reply := '\n'.join(reply):
            await ctx.reply(reply)


async def setup(bot):
    await bot.add_cog(Garbage(bot))
