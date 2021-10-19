import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True


def has_any_role(ctx):
    # is in guild, has author, and has some role besides @everyone
    return ctx.guild and ctx.author and len(ctx.author.roles) > 1

bot = commands.Bot(command_prefix="!", intents=intents)

help_command = discord.utils.get(bot.commands, name="help")
help_command.add_check(has_any_role)

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
    if not has_any_role(ctx):
        await ctx.message.reply(f"No.")
    else:
        await ctx.message.reply(f"error: {error}")

@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
