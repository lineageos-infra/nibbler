import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        bot.load_extension(f"cogs.{cog[:-3]}")

for cog in bot.cogs:
    bot.get_cog(cog).redis = bot.get_cog("Redis").redis


@bot.event
async def on_ready():
    print(f"{bot.user.name} ready")

@bot.event
async def on_command_error(ctx, error):
    await ctx.message.reply(f"error: {error}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
