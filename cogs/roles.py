from discord.ext import tasks, commands

import discord
from discord.ext.commands.errors import PrivateMessageOnly


class Roles(commands.Cog):
    '''Roles provides multiple funtions - this is where most of the permission related stuff for lineage lives.
    - makes #roles operate, see !help reactionrole
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
        self.channel = discord.utils.get(self.bot.guilds[0].channels, name="roles")
        await self.do_update()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.user.id == payload.member.id:
            return
        if payload.channel_id != self.channel.id:
            return
        # get role
        emoji = payload.emoji.name
        try:
            role = discord.utils.get(payload.member.guild.roles, name=self.redis.hget("roles", emoji).decode('utf-8'))
            if role:
                if role in payload.member.roles:
                    await payload.member.remove_roles(role, reason="clicked emoji")
                else:
                    await payload.member.add_roles(role, reason="clicked emoji")
        except:
            pass
        message = await self.channel.fetch_message(payload.message_id)
        await message.remove_reaction(emoji, payload.member)

    @commands.group(help="reaction-role config")
    @commands.is_owner()
    async def reactionrole(self, ctx):
        pass

    @reactionrole.command(name="add", help="add a role for reaction-joining")
    async def add_role(self, ctx, category: str, role: str, emoji: str, info: str):
        if not role in [x.name for x in ctx.guild.roles]:
            await ctx.guild.create_role(name=role, reason="auto created for role-reactions")
        self.redis.hset("roles", emoji, role)
        self.redis.hset("roleinfo", emoji, info)
        self.redis.hset("rolecategories", emoji, category)
        await ctx.message.add_reaction("👍")

    @reactionrole.command(name="del", help="delete a role by name")
    async def _del(self, ctx, emoji):
        self.redis.hdel("roles", emoji)
        self.redis.hdel("roleinfo", emoji)
        self.redis.hdel("rolecategories", emoji)
        await ctx.message.add_reaction("👍")

    @reactionrole.command(help="list all the roles available for reactions")
    async def get(self, ctx):
        roles = self.redis.hgetall("roles")
        info = self.redis.hgetall("roleinfo")
        categories = self.redis.hgetall("rolecategories")
        message = ""
        for k, v in roles.items():
            c = categories.get(k)
            i = info.get(k)
            message += f"{k.decode('utf-8')}: {v.decode('utf-8')} (info: {i}, category: {c})\n"


        await ctx.send(message)
        await ctx.message.add_reaction("👍")

    async def do_update(self):
        if len(self.bot.guilds) == 0:
            return
        if not hasattr(self, 'channel'):
            self.channel = discord.utils.get(self.bot.guilds[0].channels, name="roles")

        message = await self.channel.history(limit=1).flatten()
        if message:
            cmd = message[0].edit
            await message[0].clear_reactions()
        else:
            cmd = self.channel.send

        roles = self.redis.hgetall("roles")
        info = self.redis.hgetall("roleinfo")
        categories = self.redis.hgetall("rolecategories")

        content = "Some channels require roles - react below:\n"

        data = {}

        for role in roles.keys():
            if categories[role] not in data:
                data[categories[role]] = []
            data[categories[role]].append(f"{role.decode('utf-8')} {info.get(role).decode('utf-8')}")

        for k,v in data.items():
            content += f"**{k.decode('utf-8')}**\n".upper()
            for i in v:
                content += f"{i}\n"


        m = await cmd(content=content)

        # react to it with all the things
        message = await self.channel.history(limit=1).flatten()
        for k, v in roles.items():
            await message[0].add_reaction(k.decode('utf-8'))

    @reactionrole.command(help="trigger an update of the reaction-role message in #roles")
    async def update(self, ctx):
        await self.do_update()
        await ctx.message.add_reaction("👍")

    @tasks.loop(minutes=15)
    async def update_task(self):
        await self.do_update()

    @commands.command(help="Add maintainers via either a mention (@user) or a string (user)")
    @commands.has_role("Project Director")
    async def maintainer(self, ctx, *args):
        role = discord.utils.get(ctx.guild.roles, name="Maintainer")
        users = ctx.message.mentions
        for arg in args:
            u = discord.utils.get(ctx.guild.members, name=arg)
            if u:
                users.append(u)
            else:
                await ctx.reply(f"User \"{arg}\" doesn't exist in this server")
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
            await ctx.reply("This user doesn't exist in this server")
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
            await ctx.reply("This user doesn't exist in this server")
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

def setup(bot):
    bot.add_cog(Roles(bot))
