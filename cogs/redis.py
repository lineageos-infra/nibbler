import os
from discord.ext import commands

import redis as _redis

config = {
    "REDIS_HOST": os.environ.get("REDIS_HOST", "localhost"),
    "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
    "REDIS_DB": int(os.environ.get("REDIS_DB", 0)),
    "REDIS_PASSWORD": os.environ.get("REDIS_PASSWORD", None),
}


class Redis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = _redis.StrictRedis(
            host=config["REDIS_HOST"],
            port=config["REDIS_PORT"],
            db=config["REDIS_DB"],
            password=config["REDIS_PASSWORD"],
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(help="(owner only) interact with bot config redis store")
    @commands.has_role("Project Director")
    async def config(self, ctx, command, *args):
        text = getattr(self.redis, command)(*args)

        if type(text) in [list, set]:
            text = [x.decode("utf-8") for x in text]
        elif type(text) in [dict]:
            text = {x.decode("utf-8"): y.decode("utf-8") for x, y in text.items()}
        elif type(text) is bytes:
            text = text.decode("utf-8")

        await ctx.send(f"```{text}```")


async def setup(bot):
    await bot.add_cog(Redis(bot))
