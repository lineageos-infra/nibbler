from discord.ext import commands


class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @commands.command(
        help="Manage Todo Lists. Action can be one of 'list', 'add', or 'done'. Note: all list items must be quoted."
    )
    @commands.has_role('Maintainer')
    async def todo(self, ctx, _list, action, item=None):
        if action == 'list':
            items = self.redis.hgetall(f'todo:{_list}')
            reply = ''
            for k, v in items.items():
                if v.decode('utf-8') == 'done':
                    if item == 'all':
                        reply += f'{v.decode("utf-8")}: {k.decode("utf-8")}\n'
                else:
                    reply += f'{v.decode("utf-8")}: {k.decode("utf-8")}\n'
            if not reply:
                reply = 'This list is empty'
            await ctx.reply(f'```{reply}```', mention_author=False)
        elif action == 'add':
            if not item:
                ctx.reply("I can't add nothing")
                return
            self.redis.hset(f'todo:{_list}', item, ctx.message.author.name)
            await ctx.message.add_reaction('👍')
        elif action == 'done':
            if not item:
                await ctx.message.reply("I can't complete nothing")
            elif not self.redis.hget(f'todo:{_list}', item):
                await ctx.message.reply('Item not found')
            else:
                self.redis.hset(f'todo:{_list}', item, 'done')
                await ctx.message.add_reaction('👍')


async def setup(bot):
    await bot.add_cog(Todo(bot))
