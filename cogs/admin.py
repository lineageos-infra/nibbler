import os

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

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
