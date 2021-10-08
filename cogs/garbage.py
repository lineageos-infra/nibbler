from discord.ext import commands
import requests


class Garbage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(name='next', hidden=True)
    async def _next(self, ctx):
        await ctx.send("Another satisfied customer. NEXT!")

    @commands.command(hidden=True)
    async def devices(self, ctx):
        await ctx.send("Supported devices list: https://wiki.lineageos.org/devices/. Requests for additions can be made at https://undocumented.software/device_request/")
    
    @commands.command(hidden=True)
    async def catfact(self, ctx):
        req = requests.get("https://itvends.com/catfacts.php?format=text")
        await ctx.send(req.text)
    
    @commands.command(hidden=True)
    async def catfact(self, ctx):
        req = requests.get("https://itvends.com/vend.php?format=text")
        await ctx.send(f"_vends {req.text}_")


def setup(bot):
    bot.add_cog(Garbage(bot))
