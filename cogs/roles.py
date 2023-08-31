import discord
from discord.ext import tasks, commands


class Roles(commands.Cog):
    '''Roles provides multiple funtions - this is where most of the permission related stuff for lineage lives.
    - quickly add people to the maintainer role via !maintainer (mention or user)
    '''
    def __init__(self, bot):
        self.bot = bot
        self.update_task.start()

    def cog_unload(self):
        self.update_task.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(help="Add maintainers via their global user name")
    @commands.has_role("Project Director")
    async def maintainer(self, ctx, *args):
        role = discord.utils.get(ctx.guild.roles, name="Maintainer")
        users = []
        for arg in args:
            u = discord.utils.get(ctx.guild.members, name=arg)
            if u:
                users.append(u)
            else:
                await ctx.reply(f"User \"{arg}\" doesn't exist in this server. note: this _must_ be their global username, not their nick.")
        if users:
            await ctx.message.add_reaction("✅")
            for user in users:
                if not role in user.roles:
                    await user.add_roles(role)

    @commands.group(help="commands related to hardware private channels")
    async def private(self, ctx):
        pass

    @private.command(help="Create a channel under 'private'")
    @commands.has_role("Project Director")
    async def create(self, ctx, name):
        role = discord.utils.get(ctx.guild.roles, name=name)

        category = discord.utils.get(ctx.guild.categories, name='private')
        channel = discord.utils.get(ctx.guild.channels, name=name)

        if not role:
            role = await ctx.guild.create_role(name=name)

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True)
        }
        if not category:
            category = await ctx.guild.create_category_channel(name='private', overwrites=overwrites)
        else:
            await category.set_permissions(role, read_messages=True)

        if not channel or channel.category != category:
            channel = await ctx.guild.create_text_channel(name=name, category=category, overwrites=overwrites)

        await ctx.message.add_reaction("👍")

    @private.command(name="add", help="Add a user to the current room.")
    async def add_private(self, ctx, user):
        if not discord.utils.get(ctx.author.roles, name=ctx.channel.name):
            await ctx.reply("You don't have permission to do this.")
            return
        who = discord.utils.get(ctx.guild.members, name=user)
        if not who:
            await ctx.reply("This user doesn't exist in this server. note: this _must_ be their global username, not their nick")
            return
        role = discord.utils.get(ctx.guild.roles, name=ctx.channel.name)
        if not role:
            await ctx.reply("This isn't a private enough channel!")
            return
        await who.add_roles(role)
        await ctx.message.add_reaction("👍")

    @private.command(help="kick a user from the current room.")
    async def kick(self, ctx, user):
        if not discord.utils.get(ctx.author.roles, name=ctx.channel.name):
            await ctx.reply("You don't have permission to do this.")
            return
        who = discord.utils.get(ctx.guild.members, name=user)
        if not who:
            await ctx.reply("This user doesn't exist in this server. note: this _must_ be their global username, not their nick")
            return
        role = discord.utils.get(ctx.guild.roles, name=ctx.channel.name)
        if not role:
            await ctx.reply("This isn't a private enough channel!")
            return
        await who.remove_roles(role)
        await ctx.message.add_reaction("👍")

    @private.command(help="Leave the current room.")
    async def leave(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=ctx.channel.name)
        if role:
            await ctx.author.remove_roles(role)
        await ctx.message.add_reaction("👍")

async def setup(bot):
    await bot.add_cog(Roles(bot))
