from discord.commands import slash_command, Option
from lyrics_extractor import SongLyrics 
from discord.ext import commands
from bs4 import BeautifulSoup
from discord.utils import get
import lyrics_extractor
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
    currentPlayingSong = None
    playerVolume = int(config["PlayerVolume"])
    isplaying = False
    running = False
    is_paused = False
    voice_client = None
    loop_song = False

    extract_lyrics = SongLyrics(config["GCS_API_KEY"], config["GCS_ENGINE_ID"])
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
            try:
                if 'entries' in data:
                    # take first item from a playlist
                    data = data['entries'][0]
            except TypeError:
                print("Data is empty") 
            filename = data['url'] if stream else Music.ytdl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename, **Music.ffmpeg_options), data=data)

    async def music_loop(self, ctx):
        while True:
            if self.is_paused:
                print("Not playing because paused, skipping...")
            else:
                if len(self.song_queue) > 0 and not ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    player = await Music.YTDLSource.from_url(self.song_queue[0], loop=self.bot.loop, stream=True)
                    await ctx.respond('Now playing: `{}`'.format(player.title))
                    self.currentPlayingSong = player.title
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    ctx.voice_client.source.volume = self.playerVolume / 100
                    del self.song_queue[0]
            if len(self.song_queue) == 0:
                self.running = False
                await ctx.send("`Queue endet`")
                break
            await asyncio.sleep(1)

    async def loop_loop(self, ctx):
        while self.loop_song:
            if not ctx.voice_client.is_playing():
                player = await Music.YTDLSource.from_url(self.currentPlayingSong, loop=self.bot.loop, stream=True)
                await ctx.send('Now playing: `{}`'.format(player.title))
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            if not self.loop_song:
                print("stopped loop")
                break
            await asyncio.sleep(1)
            
    ##########################
    ### Commands and Events###
    ##########################
    
    @commands.Cog.listener()
    async def on_ready(self):
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
            await ctx.respond(f"[+] Already Playing - Added: `{info_dict.get('title')}`")
            self.song_queue.append(info_dict.get('title'))
            if self.running == False:
                print("started loop")
                self.task = self.bot.loop.create_task(self.music_loop(ctx=ctx))
                self.running = True
            else:
                print("Not started loop")
        else:
            msg = await ctx.respond(f"Searching `{url}`")
            player = await Music.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            await msg.edit_original_message(content='Now playing: `{}`'.format(player.title))
            self.currentPlayingSong = player.title
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            ctx.voice_client.source.volume = self.playerVolume / 100
               
    @slash_command(guild_ids=config["test_guild_id"], description="Changes the player's volume")
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        if volume >= 1 and volume <= 200:
            self.volume = volume
            ctx.voice_client.source.volume = self.playerVolume / 100
            await ctx.respond("Changed volume to `{}%`".format(volume))
        else:
            await ctx.respond(f"Versuchs gar nicht erst du Hurensohn, dein IQ beträgt: -`{volume}`")

    @slash_command(guild_ids=config["test_guild_id"], description="Skips the current playing song")
    async def skip(self, ctx):
        ctx.voice_client.stop()
        self.running = False
        if self.running == False:
            print("started loop from skip")
            self.task = self.bot.loop.create_task(self.music_loop(ctx=ctx))
            self.running = True
        else:
            print("Not started loop from skip")
    
    @slash_command(guild_ids=config["test_guild_id"], description="Pauses the music")
    async def pause(self, ctx,):
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                await ctx.respond("Music: `Paused`")
                self.is_paused = True
            elif not ctx.voice_client.is_playing() and self.is_paused:
                await ctx.respond("Im paused at the moment use `/resume` to start playing again")
            else:
                await ctx.respond("Im not playing at the moment start playing with `/play your song`")
        except AttributeError:
            await ctx.respond("I need to be in a voice channel to pause music")

    @slash_command(guild_ids=config["test_guild_id"], description="Resumes the music")
    async def resume(self, ctx,):
        try:
            if ctx.voice_client.is_paused() or self.is_paused:
                ctx.voice_client.resume()
                await ctx.respond("Music: `Resumed`")
                self.is_paused = False
            else:
                await ctx.respond("Im not paused at the moment no need to resume")
        except AttributeError:
            await ctx.respond("I need to be in a voice channel to resume music")

    @slash_command(guild_ids=config["test_guild_id"], description="Stops playing instantly (can't be resumed)")
    async def stop(self, ctx,):
        try:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.respond("Music: `Stopped`")
            else:
                await ctx.respond("Im not playing anything no need to stop")
        except AttributeError:
            await ctx.respond("I need to be in a voice channel to stop music")
    
    @slash_command(guild_ids=config["test_guild_id"], description="Loops current Track")
    async def loop(self, ctx,):
        if not self.loop_song:
            self.loop_song = True
            await ctx.respond("Loop: `Enabled`")
            self.bot.loop.create_task(self.loop_loop(ctx=ctx))
        else:
            await ctx.respond("Loop: `Disabled`")
            self.loop_song = False

    @slash_command(guild_ids=config["test_guild_id"], description="Displays the current Songs in Queue")
    async def queue(self, ctx,):
        queue = ""
        for i, song in enumerate(self.song_queue):
            queue += f"[{i}]  -  {song}\n"
        if len(self.song_queue) > 0:
            await ctx.respond(f"```{queue}```")
        else:
            await ctx.respond("Queue is empty")

    
    @slash_command(guild_ids=config["test_guild_id"], description="Displays currents playing songs lyrics")
    async def lyrics(self, ctx):
        if self.currentPlayingSong != None:
            try:
                resp = await ctx.respond(f"Fetching Lyrics for: `{self.currentPlayingSong}`")
                data = self.extract_lyrics.get_lyrics(self.currentPlayingSong)
                title, lyrics = data["title"], data["lyrics"]
                await resp.edit_original_message(content=f"► **{self.currentPlayingSong}** ◄")
                while len(lyrics) > 1500:
                    reply = await ctx.send(f"```{lyrics[:1500]}```")
                    lyrics = lyrics[1500:]
                else:
                    reply = await ctx.send(f"```{lyrics}```")
            except lyrics_extractor.LyricScraperException:
                await resp.edit_original_message(content="There are sadly no Lyrics for this song aviable")
        else:
            await ctx.respond("Nothing playing currently, start playing with `/play your song`")

    @slash_command(guild_ids=config["test_guild_id"], description="Shows currently playing song")
    async def nowplaying(self, ctx,):
        if self.currentPlayingSong != None:
            await ctx.respond(f"Currently playing `{self.currentPlayingSong}` ")
            info_dict = self.ytdl.extract_info(self.currentPlayingSong, download=False)
            # Work further here
            ##print("\n"+str(info_dict.get("len")))
        else:
            await ctx.respond(f"Not Playing anything, use `/play` to start playing")

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