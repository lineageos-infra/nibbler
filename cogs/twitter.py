from discord.ext import tasks, commands

import dateutil.parser
import discord
import requests
import sys
import urllib.parse


class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetch_posts.start()

    def cog_unload(self):
        self.fetch_posts.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {__name__}")

    @tasks.loop(seconds=30)
    async def fetch_posts(self):
        if len(self.bot.guilds) == 0:
            return

        if not hasattr(self, "channel"):
            channel = self.redis.hget("config", "twitter.channel")
            if not channel:
                print("Please !config hset config twitter.channel #channel")
                return
            channel_id = channel.decode("utf-8")[2:-1]
            self.channel = discord.utils.get(self.bot.guilds[0].channels, id=int(channel_id))

        if not hasattr(self, "done"):
            self.done = [x.decode("utf-8") for x in self.redis.lrange("twitter-fetch:done", 0, -1)]

        try:
            if False:
                headers = {
                    # https://abs.twimg.com/responsive-web/client-web/main.72c84465.js
                    "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Linux",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                }

                # get guest token
                session = requests.Session()
                request = session.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers, timeout=5)
                if request.status_code != 200:
                    print(f"Failed to get guest token (status_code: {request.status_code}, text: {request.text})",
                        file=sys.stderr)
                    return

                headers["origin"] = "https://twitter.com"
                headers["referer"] = "https://twitter.com/"
                headers["x-guest-token"] = request.json()["guest_token"]
                headers["x-twitter-active-user"] = "yes"
                headers["x-twitter-client-langua"] = "en"

                # search for newest posts mentioning @LineageAndroid
                request = session.get("https://api.twitter.com/2/search/adaptive.json?" + urllib.parse.urlencode({
                    "include_profile_interstitial_type": 1,
                    "include_blocking": 1,
                    "include_blocked_by": 1,
                    "include_followed_by": 1,
                    "include_want_retweets": 1,
                    "include_mute_edge": 1,
                    "include_can_dm": 1,
                    "include_can_media_tag": 1,
                    "include_ext_has_nft_avatar": 1,
                    "include_ext_is_blue_verified": 1,
                    "include_ext_verified_type": 1,
                    "skip_status": 1,
                    "cards_platform": "Web-12",
                    "include_cards": 1,
                    "include_ext_alt_text": "true",
                    "include_ext_limited_action_results": "false",
                    "include_quote_count": "true",
                    "include_reply_count": 1,
                    "tweet_mode": "extended",
                    "include_ext_collab_control": "true",
                    "include_ext_views": "true",
                    "include_entities": "true",
                    "include_user_entities": "true",
                    "include_ext_media_color": "true",
                    "include_ext_media_availability": "true",
                    "include_ext_sensitive_media_warning": "true",
                    "include_ext_trusted_friends_metadata": "true",
                    "send_error_codes": "true",
                    "simple_quoted_tweet": "true",
                    "q": "(@LineageAndroid)",
                    "tweet_search_mode": "live",
                    "query_source": "typed_query",
                    "count": 20,
                    "requestContext": "launch",
                    "pc": 1,
                    "spelling_corrections": 1,
                    "include_ext_edit_control": "true",
                    "ext": "mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo,editControl,collab_control,vibe",
                }, safe="@(),"), headers=headers, timeout=5)
                if request.status_code != 200:
                    print(f"Failed to get search results (status_code: {request.status_code}, text: {request.text})",
                        file=sys.stderr)
                    return
            else:
                request = requests.get("https://lineage-twtprx.uc.r.appspot.com", timeout=5)
                if request.status_code != 200:
                    print(f"Failed to get search results (status_code: {request.status_code}, text: {request.text})",
                        file=sys.stderr)
                    return

            tweets = request.json()["globalObjects"]["tweets"]
            users = request.json()["globalObjects"]["users"]

            tweet_ids = list(tweets.keys())
            tweet_ids.sort(key=lambda x: dateutil.parser.parse(tweets[x]["created_at"]))

            for tweet_id in tweet_ids:
                if tweet_id in self.done:
                    continue

                user_id_str = tweets[tweet_id]['user_id_str']
                screen_name = users[user_id_str]['screen_name']

                if '@LineageAndroid' in tweets[tweet_id]['full_text']:
                    await self.channel.send(f"https://fxtwitter.com/{screen_name}/status/{tweet_id}")
                self.redis.lpush("twitter-fetch:done", tweet_id)
                self.redis.ltrim("twitter-fetch:done", 0, 99)
                self.done = [tweet_id, *self.done[:99]]
        except:
            pass

    @commands.group()
    @commands.has_role("Project Director")
    async def twitter(self, ctx):
        pass

    @twitter.command()
    @commands.has_role("Project Director")
    async def flush(self, ctx):
        await ctx.message.delete()
        self.redis.delete("twitter-fetch:done")
        self.done = []


def setup(bot):
    bot.add_cog(Twitter(bot))
