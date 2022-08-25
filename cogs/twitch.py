from discord.commands import slash_command, Option 
from discord.ext import commands
import requests
import asyncio
import discord
import json
import os




class Twitch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    os.chdir(os.path.dirname(__file__))

    with open("../config.json", "r") as config:
        config = json.load(config)


    
    async def twitch_live_check(self, twitch_broadcaster: list = config['twitch_broadcaster']):
        #counter = 0
        streamers = {}
        streamer_state = {
            "live": False,
            "sent_msg": False
        }

        for live_streamer in twitch_broadcaster:
            streamers[live_streamer['name']] = streamer_state.copy()

        while True:
            #print(f"Loop ran: {counter}")
            #counter +=1

            for live_streamer in twitch_broadcaster:
                
                contents = requests.get(f'https://www.twitch.tv/{live_streamer["name"]}').content.decode('utf-8')
                
                if 'isLiveBroadcast' in contents:
                    streamers[live_streamer['name']]["live"] = True
                else:
                    streamers[live_streamer['name']]["live"] = False
                    streamers[live_streamer['name']]["sent_msg"] = False

                if streamers[live_streamer['name']]["live"] and not streamers[live_streamer['name']]["sent_msg"]:
                    for channel in self.config['twitch_promotion_channel_ids']:
                        channel = self.bot.get_channel(channel)
                        dc_user = f"<@{live_streamer['dc_user_id']}>" if live_streamer['dc_user_id'] != 'NONE' else live_streamer['name']
                        await channel.send(self.config['twitch_promotion_message'].replace("%streamer%", live_streamer['name']).replace("%dc_user%", str(dc_user)))
                        streamers[live_streamer['name']]["sent_msg"] = True

            await asyncio.sleep(20)

    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.loop.create_task(self.twitch_live_check(twitch_broadcaster=self.config['twitch_broadcaster']))




def setup(bot):
    bot.add_cog(Twitch(bot))

    