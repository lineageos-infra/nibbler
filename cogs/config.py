import os
import time
from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def config(self, ctx, command, key, args=None):
        if args:
            text = getattr(self.redis, command)(key, args)
        else:
            text = getattr(self.redis, command)(key)

        if type(text) in [list, set]:
            text = [x.decode("utf-8") for x in text]
        elif type(text) in [dict]:
            text = {x.decode("utf-8"): y.decode("utf-8") for x, y in text.items()}
        elif type(text) is bytes:
            text = text.decode("utf-8")

        await ctx.send(f"```{text}```")


def setup(bot):
    bot.add_cog(Config(bot))
