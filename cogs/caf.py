import asyncio
import io
import json
import uuid

import discord
from discord.ext import commands, tasks


class CAF(commands.Cog):
    CLO_URL_PREFIX = 'https://git.codelinaro.org/clo/la'

    def __init__(self, bot):
        self.bot = bot
        self.fetch_tags.start()

    def cog_unload(self):
        self.fetch_tags.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @tasks.loop(hours=1)
    async def fetch_tags(self):
        if len(self.bot.guilds) == 0:
            return

        if not hasattr(self, 'channel'):
            channel = self.redis.hget('config', 'caf.channel')
            if not channel:
                print('Please !config hset config caf.channel #channel')
                return
            channel_id = channel.decode('utf-8')[2:-1]
            self.channel = discord.utils.get(
                self.bot.guilds[0].channels, id=int(channel_id)
            )

        for key, value in self._tracked().items():
            tags = await self._get_tags(value['url'])
            new_tag = next(
                (x for x in tags if x.startswith(value['prefix'])), None
            )

            if not new_tag or value['tag'] == new_tag:
                continue

            value['tag'] = new_tag
            self.redis.hset('caf-fetch:tracked', key, json.dumps(value))

            embed = discord.Embed(
                title='New tag spotted',
                url=f'{value["url"]}/-/tree/{value["tag"]}',
            )
            embed.add_field(name='Tag', value=value['tag'], inline=False)
            embed.add_field(name='URL', value=value['url'], inline=False)
            await self.channel.send(embed=embed)

    @commands.group()
    @commands.has_role('Maintainer')
    async def caf(self, ctx):
        pass

    @staticmethod
    async def _get_tags(url):
        proc = await asyncio.create_subprocess_exec(
            'timeout',
            '5',
            'git',
            'ls-remote',
            '--refs',
            '--tags',
            url.replace('https://', 'https://:@'),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout = await proc.stdout.read()

        tags = []

        for line in stdout.decode().splitlines():
            _, ref = line.split()
            tags.append(ref[10:])

        return tags[::-1]

    def _tracked(self):
        tracked = {}

        for key, value in self.redis.hscan_iter('caf-fetch:tracked'):
            tracked[key.decode()] = json.loads(value)

        return tracked

    @caf.command()
    @commands.has_role('Maintainer')
    async def track(self, ctx, url, prefix):
        assert url.startswith(self.CLO_URL_PREFIX), 'Invalid URL'
        self.redis.hset(
            'caf-fetch:tracked',
            str(uuid.uuid4()),
            json.dumps({'url': url, 'prefix': prefix, 'tag': None}),
        )
        await ctx.message.add_reaction('👍')
        await self.fetch_tags()

    @caf.command()
    @commands.has_role('Maintainer')
    async def untrack(self, ctx, url, prefix=None):
        for key, value in self._tracked().items():
            if value['url'] != url:
                continue
            if prefix and value['prefix'] != prefix:
                continue
            self.redis.hdel('caf-fetch:tracked', key)
        await ctx.message.add_reaction('👍')

    @caf.command()
    @commands.has_role('Maintainer')
    async def tracked(self, ctx):
        response = []

        for _, value in self._tracked().items():
            response.append(f'{value["url"]} {value["prefix"]} {value["tag"]}')

        await ctx.reply(
            file=discord.File(
                io.StringIO('\n'.join(sorted(response))), filename='tracked.txt'
            )
        )


async def setup(bot):
    await bot.add_cog(CAF(bot))
