import asyncio
import datetime
import os

import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.redis.get('admin.auto_timeout') != b'1':
            return

        utc_now = datetime.datetime.now(datetime.timezone.utc)

        if member.created_at > utc_now - datetime.timedelta(days=1):
            print('Timing out fresh account:', member.name)
            await asyncio.sleep(60 * 8)
            await member.timeout(utc_now + datetime.timedelta(days=7))

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        message = await ctx.send('Reloading!')
        await ctx.message.delete()
        try:
            cogs = os.listdir('./cogs')
            for cog in cogs:
                if cog.endswith('.py'):
                    await self.bot.reload_extension(f'cogs.{cog[:-3]}')

        except Exception as e:
            await message.edit(content=f'Error: {e}', delete_after=10)
        else:
            await message.edit(content='Reloaded!', delete_after=10)


async def setup(bot):
    await bot.add_cog(Admin(bot))
