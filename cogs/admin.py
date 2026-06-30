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
            await member.timeout(
                utc_now + datetime.timedelta(days=7), reason='Fresh account'
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # We only care about #human-spam here
        if message.channel.id != 1141822511902900446:
            return

        print('Nuking potential spammer:', message.author.name)

        # Timeout for 7 days
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        await message.author.timeout(
            utc_now + datetime.timedelta(days=7), reason='Posted in #human-spam'
        )

        # Delete last 10 minutes of their messages
        cutoff = utc_now - datetime.timedelta(minutes=10)

        for channel in message.guild.text_channels:
            if channel.category_id not in [
                628008281121751070,  # Public (Linked to IRC)
                1141822171992309901,  # Public (Discord only)
            ]:
                continue

            try:
                await channel.purge(
                    check=lambda m: m.author == message.author,
                    after=cutoff,
                    bulk=True,
                    reason='Posted in #human-spam',
                )
            except Exception as e:
                print('Purge failed', e)

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
