import os
from discord.ext import commands

import redis as _redis

config = {
    "REDIS_HOST": os.environ.get("REDIS_HOST", "localhost"),
    "REDIS_PORT": int(os.environ.get("REDIS_PORT", 6379)),
    "REDIS_DB": int(os.environ.get("REDIS_DB", 0)),
}


class Redis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = _redis.StrictRedis(
            host=config["REDIS_HOST"],
            port=config["REDIS_PORT"],
            db=config["REDIS_DB"],
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")


def setup(bot):
    bot.add_cog(Redis(bot))
