from discord.ext import tasks, commands

import discord


class Roles(commands.Cog):
    '''Roles provides two funtions - role reactions and a few random commands
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

    @commands.group()
    @commands.is_owner()
    async def roles(self, ctx):
        pass

    @roles.command()
    async def add(self, ctx, category, role, emoji, info):
        await ctx.message.delete()
        if not role in [x.name for x in ctx.guild.roles]:
            await ctx.guild.create_role(name=role, reason="auto created for role-reactions")
        self.redis.hset("roles", emoji, role)
        self.redis.hset("roleinfo", emoji, info)
        self.redis.hset("rolecategories", emoji, category)

    @roles.command(name="del")
    async def _del(self, ctx, emoji):
        await ctx.message.delete()
        self.redis.hdel("roles", emoji)
        self.redis.hdel("roleinfo", emoji)
        self.redis.hdel("rolecategories", emoji)

    @roles.command()
    async def get(self, ctx):
        await ctx.message.delete()
        roles = self.redis.hgetall("roles")
        info = self.redis.hgetall("roleinfo")
        categories = self.redis.hgetall("rolecategories")
        message = ""
        for k, v in roles.items():
            c = categories.get(k)
            i = info.get(k)
            message += f"{k.decode('utf-8')}: {v.decode('utf-8')} (info: {i}, category: {c})\n"

    
        await ctx.send(message, delete_after=20)
    
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

        content = "Some channels requires roles - react below:\n"
        
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

    @roles.command()
    async def update(self, ctx):
        await ctx.message.delete()
        await self.do_update()

    @tasks.loop(minutes=15)
    async def update_task(self):
        await self.do_update()
    
    # adds someone to maintainer role
    @commands.command()
    @commands.has_role("Project Director")
    async def maintainer(self, ctx, user):
        role = discord.utils.get(ctx.guild.roles, name="Maintainer")
        for user in ctx.message.mentions:
            if not role in user.roles:
                await user.add_roles(role)
                await ctx.message.add_reaction("✔️")
    
def setup(bot):
    bot.add_cog(Roles(bot))
