import os
import uuid
from datetime import datetime

import requests
from discord.ext import commands


class Buildkite(commands.Cog):
    """Buildkite launches builds"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded {__name__}')

    @commands.group(help='manage buildkite jobs')
    async def buildkite(self, ctx):
        pass

    @commands.has_role('Project Director')
    @buildkite.command(
        name='build',
        help='build android. example: mako,hammerhead lineage-20.0#c856ad1,build1 experimental 123456 234567',
    )
    async def build(
        self,
        ctx,
        devices: str,
        version: str,
        release_type: str = 'nightly',
        *args,
    ):
        for device in devices.split(','):
            tags = version.split(',')
            if '#' in tags[0]:
                branch, commit = tags[0].split('#')
            else:
                branch = tags[0]
                commit = 'HEAD'
            host = tags[1] if len(tags) > 1 else ''
            message = f'{device} {datetime.today().strftime("%Y%m%d")}'
            if release_type == 'experimental':
                message = (
                    f':rotating_light: EXPERIMENTAL :rotating_light: {message}'
                )
            data = {
                'branch': branch,
                'commit': commit,
                'message': message,
                'env': {
                    'DEVICE': device,
                    'HOST': host,
                    'RELEASE_TYPE': release_type,
                    'TYPE': 'userdebug',
                    'VERSION': branch,
                    'BUILD_UUID': str(uuid.uuid4()).replace('-', ''),
                    'EXP_PICK_CHANGES': ' '.join(args),
                },
            }

            resp = requests.post(
                'https://api.buildkite.com/v2/organizations/lineageos/pipelines/android/builds',
                json=data,
                headers={
                    'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
                },
            )
            if resp.status_code == 201:
                await ctx.message.reply(f'started: {resp.json()["web_url"]}')
            else:
                await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Project Director')
    @commands.command(
        name='build',
        help='build android. example: mako lineage-20.0 experimental 123456 234567',
    )
    async def _build(
        self,
        ctx,
        device: str,
        version: str,
        release_type: str = 'nightly',
        *args,
    ):
        await self.build(ctx, device, version, release_type, *args)

    @commands.has_role('Maintainer')
    @buildkite.command(name='rebuild', help='rebuild 12345')
    async def rebuild(self, ctx, build_id: str, *args):
        resp = requests.put(
            f'https://api.buildkite.com/v2/organizations/lineageos/pipelines/android/builds/{build_id}/rebuild',
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 200:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Maintainer')
    @buildkite.command(name='cancel', help='cancel 12345')
    async def cancel(self, ctx, build_id: str, *args):
        resp = requests.put(
            f'https://api.buildkite.com/v2/organizations/lineageos/pipelines/android/builds/{build_id}/cancel',
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 200:
            await ctx.message.reply(f'canceled: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Project Director')
    @commands.command(
        name='crowdin',
        help='start crowdin build for a branch. example: lineage-20.0',
    )
    async def crowdin(self, ctx, version: str):
        data = {
            'branch': version,
            'commit': 'HEAD',
            'message': 'Upload sources',
            'env': {
                'UPLOAD_SOURCES': '1',
            },
        }

        resp = requests.post(
            'https://api.buildkite.com/v2/organizations/lineageos/pipelines/crowdin/builds',
            json=data,
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 201:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')
            return

        data['message'] = 'Download new translations'
        del data['env']

        resp = requests.post(
            'https://api.buildkite.com/v2/organizations/lineageos/pipelines/crowdin/builds',
            json=data,
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 201:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Project Director')
    @buildkite.command(
        name='forcepush',
        help='force push a branch. example: hudson main https://github.com/lineageos/hudson main',
    )
    async def forcepush(
        self, ctx, repo: str, branch: str, src_repo: str, src_branch: str
    ):
        data = {
            'branch': 'main',
            'commit': 'HEAD',
            'env': {
                'REPO': f'LineageOS/{repo}',
                'DEST_BRANCH': branch,
                'SRC_REPO': src_repo,
                'SRC_BRANCH': src_branch,
            },
            'message': f'forcepush of {repo} by {ctx.message.author.name}',
        }
        resp = requests.post(
            'https://api.buildkite.com/v2/organizations/lineageos/pipelines/forcepush/builds',
            json=data,
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 201:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Project Director')
    @buildkite.command(
        name='remove',
        help='remove a build from the mirror. example: remove mako 20230714',
    )
    async def remove(self, ctx, device: str, date: str):
        data = {
            'branch': 'main',
            'commit': 'HEAD',
            'env': {'DEVICE': device, 'DATE': date},
            'message': f'removal of {device} {date} by {ctx.message.author.name}',
        }
        resp = requests.post(
            'https://api.buildkite.com/v2/organizations/lineageos/pipelines/mirror-remove/builds',
            json=data,
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 201:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    async def _mirror_toggle(self, ctx, env: dict, message: str):
        data = {
            'branch': 'main',
            'commit': 'HEAD',
            'env': env,
            'message': message,
        }
        resp = requests.post(
            'https://api.buildkite.com/v2/organizations/lineageos/pipelines/mirror-toggle/builds',
            json=data,
            headers={
                'Authorization': f'Bearer {os.environ.get("BUILDKITE_TOKEN")}'
            },
        )
        if resp.status_code == 201:
            await ctx.message.reply(f'started: {resp.json()["web_url"]}')
        else:
            await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')

    @commands.has_role('Project Director')
    @buildkite.command(
        name='mirror-enable',
        help='enable given mirror. example: mirror-enable mirrors.dotsrc.org',
    )
    async def mirror_enable(self, ctx, mirror: str):
        await self._mirror_toggle(
            ctx,
            {'ACTION': 'enable', 'MIRROR': mirror},
            f'Enabling {mirror} by {ctx.message.author.name}',
        )

    @commands.has_role('Project Director')
    @buildkite.command(
        name='mirror-disable',
        help='disable given mirror. example: mirror-disable mirrors.dotsrc.org',
    )
    async def mirror_disable(self, ctx, mirror: str):
        await self._mirror_toggle(
            ctx,
            {'ACTION': 'disable', 'MIRROR': mirror},
            f'Disabling {mirror} by {ctx.message.author.name}',
        )

    @commands.has_role('Project Director')
    @buildkite.command(
        name='mirror-list',
        help='list mirrors',
    )
    async def mirror_list(self, ctx):
        await self._mirror_toggle(
            ctx,
            {'ACTION': 'disable'},
            f'Listing mirrors by {ctx.message.author.name}',
        )


async def setup(bot):
    await bot.add_cog(Buildkite(bot))
