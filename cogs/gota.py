import asyncio
import binascii
import gzip
import io
import os
import random

import discord
import requests
from discord.ext import commands

from proto import checkin_generator_pb2


class GoogleOTA(commands.Cog):
    HEADERS = {
        'accept-encoding': 'gzip, deflate',
        'content-encoding': 'gzip',
        'content-type': 'application/x-protobuffer',
    }

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @commands.command(hidden=True)
    async def gota(self, ctx, fingerprint):
        checkin_request = checkin_generator_pb2.AndroidCheckinRequest()
        checkin_request.imei = self.generate_imei()
        checkin_request.id = 0
        checkin_request.digest = self.generate_digest()
        checkin_request.checkin.build.id = fingerprint
        checkin_request.checkin.build.timestamp = 0
        checkin_request.checkin.build.device = fingerprint.split('/')[2].split(':')[0]
        checkin_request.checkin.lastCheckinMsec = 0
        checkin_request.checkin.roaming = "WIFI::"
        checkin_request.checkin.userNumber = 0
        checkin_request.checkin.deviceType = 2
        checkin_request.checkin.voiceCapable = False
        checkin_request.checkin.unknown19 = "WIFI"
        checkin_request.locale = 'en-US'
        checkin_request.macAddr.append(self.generate_mac())
        checkin_request.timeZone = 'America/New_York'
        checkin_request.version = 3
        checkin_request.serialNumber = self.generate_serial()
        checkin_request.macAddrType.append('wifi')
        checkin_request.fragment = 0
        checkin_request.userSerialNumber = 0
        checkin_request.fetchSystemUpdates = 1
        checkin_request.unknown30 = 0

        data = io.BytesIO()

        with gzip.GzipFile(fileobj=data, mode='wb') as f:
            f.write(checkin_request.SerializeToString())

        resp = requests.post('https://android.googleapis.com/checkin',
                             data=data.getvalue(),
                             headers=self.HEADERS)

        checkin_response = checkin_generator_pb2.AndroidCheckinResponse.FromString(resp.content)
        setting = {entry.name: entry.value for entry in checkin_response.setting}
        update_title = setting.get(b'update_title', b'')
        update_url = setting.get(b'update_url', b'')

        if update_title and update_url:
            embed = discord.Embed(title=update_title.decode())
            embed.add_field(name="URL", value=update_url.decode(), inline=False)
            await self.reply_and_delete(ctx, content=None, embed=embed)
        else:
            await self.reply_and_delete(ctx, content='Not found :(')

    @staticmethod
    def generate_imei():
        imei = [random.randint(0, 9) for _ in range(15)]
        return ''.join(map(str, imei))

    @staticmethod
    def generate_mac():
        return binascii.b2a_hex(os.urandom(6))

    @staticmethod
    def generate_serial():
        serial = [random.choice('0123456789abcdef') for _ in range(8)]
        return ''.join(serial)

    @staticmethod
    def generate_digest():
        digest = [random.choice('0123456789abcdef') for _ in range(40)]
        return '1-' + ''.join(digest)

    @staticmethod
    async def reply_and_delete(ctx, *args, **kwargs):
        message = await ctx.reply(*args, **kwargs)
        await asyncio.sleep(60)
        await message.delete()
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(GoogleOTA(bot))
