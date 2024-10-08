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
        # is in guild, has author, and has some role besides public ones
        public_roles = [
            "@everyone",
            "europe",
            "americas",
            "asia-australia",
        ]
        return ctx.guild and ctx.author and any([x.name not in public_roles for x in ctx.author.roles])

    async def setup_hook(self):
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        for cog in self.cogs:
            self.get_cog(cog).redis = self.get_cog("Redis").redis


bot = Bot(command_prefix="!", allowed_mentions=discord.AllowedMentions.none(), intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user.name} ready")

@bot.event
async def on_command_error(ctx, error):
    if not bot.has_any_role(ctx):
        await ctx.message.reply(f"No.")
    else:
        await ctx.message.reply(f"error: {error}")

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
