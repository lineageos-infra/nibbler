import os

import requests
from discord.ext import commands


class Gitlab(commands.Cog):
    GROUP_ID = 3905616

    GITLAB_BASE_URL = "https://gitlab.com/api/v4"
    ACCESS_REQUESTS_BASE_URL = f"{GITLAB_BASE_URL}/groups/{GROUP_ID}/access_requests"

    GITLAB_HEADERS = {
        "PRIVATE-TOKEN": os.environ.get('GITLAB_TOKEN'),
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.group(help="manage gitlab membership")
    async def gitlab(self, ctx):
        pass

    def _access_requests(self):
        return requests.get(self.ACCESS_REQUESTS_BASE_URL, headers=self.GITLAB_HEADERS).json()

    @commands.has_role("Project Director")
    @gitlab.command(help="list access requests")
    async def list(self, ctx):
        access_requests = []

        for request in self._access_requests():
            access_requests.append(f"* [{request['username']}](<{request['web_url']}>)")

        if access_requests:
            await ctx.message.reply("\n".join(access_requests))
        else:
            await ctx.message.reply("No access requests.")

    @commands.has_role("Project Director")
    @gitlab.command(help="approve an access request")
    async def approve(self, ctx, username: str):
        for request in self._access_requests():
            if request['username'] == username:
                resp = requests.put(f"{self.ACCESS_REQUESTS_BASE_URL}/{request['id']}/approve",
                                    headers=self.GITLAB_HEADERS)

                if resp.status_code != 201:
                    await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')
                else:
                    await ctx.message.add_reaction("👍")

                break
        else:
            await ctx.message.add_reaction("👎")

    @commands.has_role("Project Director")
    @gitlab.command(help="deny an access request")
    async def deny(self, ctx, username: str):
        for request in self._access_requests():
            if request['username'] == username:
                resp = requests.delete(f"{self.ACCESS_REQUESTS_BASE_URL}/{request['id']}",
                                       headers=self.GITLAB_HEADERS)

                if resp.status_code != 204:
                    await ctx.message.reply(f'failed: ```{resp.text[:1500]}```')
                else:
                    await ctx.message.add_reaction("👍")

                break
        else:
            await ctx.message.add_reaction("👎")


async def setup(bot):
    await bot.add_cog(Gitlab(bot))
