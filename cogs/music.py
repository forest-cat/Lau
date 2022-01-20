from discord.commands import slash_command, Option 
from discord.ext import commands
from bs4 import BeautifulSoup
from discord.utils import get
import youtube_dl
import requests
import discord
import asyncio
import urllib
import string
import json
import time
import os
import re



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    print(os.path.dirname(__file__))
    os.chdir(os.path.dirname(__file__))

    with open("../config.json", "r") as config:
        config = json.load(config)

    ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    ffmpeg_options = {
    'options': '-vn'
    }
    
    song_queue = []
    isplaying = False
    running = False
    voice_client = None

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = data.get('url')

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: Music.ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]
            filename = data['url'] if stream else Music.ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **Music.ffmpeg_options), data=data)

    async def music_loop(self, ctx):
        while True:
            print(len(self.song_queue))
            print(self.voice_client.is_playing())
            if len(self.song_queue) > 0 and not ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                player = await Music.YTDLSource.from_url(self.song_queue[0], loop=self.bot.loop, stream=True)
                await ctx.respond('Now playing: {}'.format(player.title))
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                ctx.voice_client.source.volume = 10 / 100
                del self.song_queue[0]
            if len(self.song_queue) == 0:
                self.running = False
                print("stopping loop")
                break
            await asyncio.sleep(3)
            print("loop running")
            
    ##########################
    ### Commands and Events###
    ##########################
    
    @commands.Cog.listener()
    async def on_ready(self):
        #self.bot.loop.create_task(self.music_loop())
        pass

    @slash_command(guild_ids=config["test_guild_id"], description="Plays the Song you put after the command.")
    async def play(self, ctx, *, url):
        if self.voice_client == None:
            self.voice_client = ctx.voice_client
        if ctx.voice_client.is_playing():
            self.ctx = ctx
            info_dict = self.ytdl.extract_info(url, download=False)
            if 'entries' in info_dict:
                # take first item from a playlist
                info_dict = info_dict['entries'][0]
            await ctx.respond("[+] Already Playing - Adding to queue")
            self.song_queue.append(info_dict.get('title'))
            if self.running == False:
                print("started loop")
                self.task = self.bot.loop.create_task(self.music_loop(ctx=ctx))
                self.running = True
            else:
                print("Not started loop")
        else:
            await ctx.respond(f"Searching {url}")
            player = await Music.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            await ctx.respond('Now playing: {}'.format(player.title))
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = 10 / 100
            
        

            
    
        # self.song_queue.append(url)
        # print(self.song_queue)
        # await ctx.send(f"[+] added {url} to Queue")

    @slash_command(guild_ids=config["test_guild_id"], description="skips current song")
    async def skip(self, ctx):
        ctx.voice_client.stop()
        self.running = False
        if self.running == False:
            print("started loop from skip")
            self.task = self.bot.loop.create_task(self.music_loop(ctx=ctx))
            self.running = True
        else:
            print("Not started loop from skip")
            
        
    @slash_command(guild_ids=config["test_guild_id"], description="Changes the player's volume")
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        if volume >= 1 and volume <= 200:
            ctx.voice_client.source.volume = volume / 100
            await ctx.respond("Changed volume to {}%".format(volume))
        else:
            await ctx.respond(f"Versuchs gar nicht erst du Hurensohn, dein IQ beträgt: {volume}")
    

    @slash_command(guild_ids=config["test_guild_id"], description="prints the queue")
    async def queue(self, ctx,):
        await ctx.respond(self.song_queue)
            
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                ctx.voice_client.stop()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        
    

def setup(bot):
    bot.add_cog(Music(bot))