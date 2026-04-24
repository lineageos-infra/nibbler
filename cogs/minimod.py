import datetime
import re

import discord
from discord.ext import commands


class MiniMod(commands.Cog):
    ALLOWED_ROLES = [
        'Moderator',
    ]
    ALLOWED_USERS = [
        717034948036526180,
    ]
    PUBLIC_ROLES = [
        '@everyone',
        'europe',
        'americas',
        'asia-australia',
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @staticmethod
    def is_allowed(ctx):
        if any(
            [x.name in MiniMod.ALLOWED_ROLES for x in ctx.message.author.roles]
        ):
            return True
        if ctx.message.author.id in MiniMod.ALLOWED_USERS:
            return True
        return False

    @commands.check(is_allowed)
    @commands.command(hidden=True)
    async def timeout(self, ctx, user: discord.Member, duration: int):
        if any([x.name not in self.PUBLIC_ROLES for x in user.roles]):
            await ctx.message.add_reaction('❌')
            return
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if re.match(r'^\d+s$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(seconds=int(duration[:-1]))
            )
            await ctx.message.add_reaction('👍')
        elif re.match(r'^\d+m$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(minutes=int(duration[:-1]))
            )
            await ctx.message.add_reaction('👍')
        elif re.match(r'^\d+d$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(days=int(duration[:-1]))
            )
            await ctx.message.add_reaction('👍')
        else:
            await ctx.message.add_reaction('❌')


async def setup(bot):
    await bot.add_cog(MiniMod(bot))
