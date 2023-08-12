from discord.ext import commands


class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    async def get_superuser_roles(self):
        return [x.decode("utf-8") for x in self.redis.smembers("superuser_roles")]

    @commands.command(help="echo raw text")
    async def echo(self, ctx):
        await ctx.reply(f"```{ctx.message}\n{ctx.message.content}```")


async def setup(bot):
    await bot.add_cog(Util(bot))
