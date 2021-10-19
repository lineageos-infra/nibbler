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
    async def vend(self, ctx):
        req = requests.get("https://itvends.com/vend.php?format=text")
        await ctx.send(f"_vends {req.text}_")

    @commands.command(hidden=True)
    async def ask(self, ctx):
        await ctx.send("Yes - you can ask questions here - you just did! Please get to the point, we don't have all day.")

    @commands.command(hidden=True)
    async def why(self, ctx):
        await ctx.send("Because, that's why.")

    @commands.command(hidden=True)
    async def yw(self, ctx):
        await ctx.send("You're welcome")

    @commands.command(hidden=True)
    async def how(send, ctx):
        await ctx.send("Stop asking questions you'll go blind.")

    @commands.command(hidden=True)
    async def what(send, ctx):
        await ctx.send("https://tenor.com/view/goat-scary-animal-crazy-animal-scary-goat-wtf-gif-5548755")


def setup(bot):
    bot.add_cog(Garbage(bot))
