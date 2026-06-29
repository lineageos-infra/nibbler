from __future__ import annotations

import datetime
import re

import discord
from discord.ext import commands


class MiniMod(commands.Cog):
    ALLOWED_ROLES = [
        'Maintainer',
        'Moderator',
    ]
    ALLOWED_USERS = [
        453576904226635787,
        717034948036526180,
    ]
    DISALLOWED_USERS = [
        438758875093532673,
    ]
    PUBLIC_ROLES = [
        '@everyone',
        'americas',
        'asia-australia',
        'europe',
        'offtopic-only',
    ]
    BRIDGE_WEBHOOK_IDS = [
        896248182802112582,
        896334981767524404,
        897609600403116092,
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @staticmethod
    def is_allowed(ctx):
        if ctx.message.author.id in MiniMod.DISALLOWED_USERS:
            return False
        if any(
            [x.name in MiniMod.ALLOWED_ROLES for x in ctx.message.author.roles]
        ):
            return True
        if ctx.message.author.id in MiniMod.ALLOWED_USERS:
            return True
        return False

    @commands.command(hidden=True)
    async def purge(
        self, ctx, user: discord.Member | discord.User | str, limit: int
    ):
        messages = []

        async for message in ctx.channel.history(limit=200):
            if message.author == user or (
                user == f'<@{message.webhook_id}>'
                and message.webhook_id in self.BRIDGE_WEBHOOK_IDS
            ):
                messages.append(message)

            if len(messages) == limit:
                break

        await ctx.channel.delete_messages(
            messages, reason=f'Removed by {ctx.message.author.name}'
        )
        await ctx.message.add_reaction('👍')

    @commands.check(is_allowed)
    @commands.command(hidden=True)
    async def timeout(self, ctx, user: discord.Member, duration: str):
        if any([x.name not in self.PUBLIC_ROLES for x in user.roles]):
            await ctx.message.add_reaction('❌')
            return
        reason = f'Timed out by {ctx.message.author.name}'
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if re.match(r'^\d+s$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(seconds=int(duration[:-1])),
                reason=reason,
            )
            await ctx.message.add_reaction('👍')
        elif re.match(r'^\d+m$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(minutes=int(duration[:-1])),
                reason=reason,
            )
            await ctx.message.add_reaction('👍')
        elif re.match(r'^\d+h$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(hours=int(duration[:-1])),
                reason=reason,
            )
            await ctx.message.add_reaction('👍')
        elif re.match(r'^\d+d$', duration):
            await user.timeout(
                utc_now + datetime.timedelta(days=int(duration[:-1])),
                reason=reason,
            )
            await ctx.message.add_reaction('👍')
        else:
            await ctx.message.add_reaction('❌')

    @commands.check(is_allowed)
    @commands.command(hidden=True)
    async def untimeout(self, ctx, user: discord.Member):
        if any([x.name not in self.PUBLIC_ROLES for x in user.roles]):
            await ctx.message.add_reaction('❌')
            return
        await user.timeout(
            None, reason=f'Timeout removed by {ctx.message.author.name}'
        )
        await ctx.message.add_reaction('👍')


async def setup(bot):
    await bot.add_cog(MiniMod(bot))
