from discord.ext import commands
import discord

class Karma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    def _get_all_points(self):
        return {discord.utils.get(x.decode("utf-8")): y.decode("utf-8") for x,y in self.redis.hgetall("points").items()}

    def _get_point(self, uid):
        value = self.redis.hget("points", uid)
        return 0 if not value else int(value)

    def _set_point(self, uid, value):
        self.redis.hset("points", uid, value)

    @commands.command(help="Get your own karma")
    async def karma(self, ctx):
        user = ctx.author.id
        points = self._get_all_points()
        values = {}
        for user, score in points.items():
            values.setdefault(score, []).append(user)
        text = []
        for score in sorted(values.keys(), reverse=True):
            text.append(f"{score}")

        text = "\n".join(text)
        await ctx.reply("You have " + text + " point(s)!", mention_author=False)

    @commands.command(help="Grants a user a point. Usage: `!point @user#0000`")
    async def point(self, ctx):
        try:
            uid = ctx.message.mentions[0].id
            if uid == ctx.message.author.id:
                points = self._get_point(uid) - 1
                text = f"You lost a point! Stop being narcissistic!\nNew score: {points}"
                self._set_point(uid, points)
            elif not uid:
                text = "User not found!"
            else:
                points = self._get_point(uid) + 1
                self._set_point(uid, points)
                text = f"Point granted to <@{ctx.message.mentions[0].id}>!\nNew score: {points}"
            await ctx.reply(text, mention_author=False)
        except Exception:
            await ctx.reply("Grants a user a point. Usage: `!point @user#0000`", mention_author=False)

    @commands.command(help="Licks a user. Usage: `!lick @user#0000`")
    async def lick(self, ctx):
        try:
            uid = ctx.message.mentions[0].id
            points = self._get_point(uid) - 1
            self._set_point(uid, points)
            text = f"{ctx.author.mention} has licked <@{ctx.message.mentions[0].id}>, losing a point!\nNew score: {points}"
            await ctx.reply(text)
        except Exception:
            await ctx.reply("Licks a user. Usage: `!lick @user#0000`", mention_author=False)

def setup(bot):
    bot.add_cog(Karma(bot))