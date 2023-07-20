import discord
from discord.ext import tasks, commands
import os
import requests

class Buildkite(commands.Cog):
    '''Buildkite launches builds
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.group(help="manage buildkite jobs")
    @commands.has_role("Project Director")
    async def buildkite(self, ctx):
        pass

    @buildkite.command(name="forcepush", help="force push a branch. example: hudson#main https://github.com/lineageos/hudson#main")
    async def forcepush(self, ctx, dest: str, src: str):
        repo, branch = dest.split("#")
        src_repo, src_branch = src.split("#")
        data = {'branch': 'main', 'commit': 'HEAD', 'env': {'REPO': f'LineageOS/{repo}', 'DEST_BRANCH': branch, 'SRC_REPO': src_repo, 'SRC_BRANCH': src_branch}, message: f'forcepush of {repo} by {ctx.message.author.name}'}
        resp = requests.post('https://buildkite.com/v2/organizations/LineageOS/pipelines/forcepush/builds', json=data, headers={"Authorization", "Bearer {os.environ.get('BUILDKITE_TOKEN')"})
        if resp.status_code == 201:
            ctx.message.reply(f"started: {resp.json()['web_url']}")
