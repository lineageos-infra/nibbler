import asyncio
import os

import discord
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, command_prefix, *, intents, **options):
        super().__init__(command_prefix, intents=intents, **options)

        help_command = discord.utils.get(self.commands, name="help")
        help_command.add_check(self.has_any_role)

    @staticmethod
    def has_any_role(ctx):
        # is in guild, has author, and has some role besides @everyone
        return ctx.guild and ctx.author and len(ctx.author.roles) > 1

    async def setup_hook(self):
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        for cog in self.cogs:
            self.get_cog(cog).redis = self.get_cog("Redis").redis


bot = Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user.name} ready")

@bot.event
async def on_command_error(ctx, error):
    if not has_any_role(ctx):
        await ctx.message.reply(f"No.")
    else:
        await ctx.message.reply(f"error: {error}")

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
