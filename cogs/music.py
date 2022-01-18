import queue
from discord.commands import slash_command, Option 
from discord.ext import commands
from discord.utils import get
import youtube_dl
import discord
import asyncio
import json
import os


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
    queue = []

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



    @slash_command(guild_ids=config["test_guild_id"], description="Plays the Song you put after the command.")
    async def play(self, ctx, *, url):
        # Queue Feature
        # if ctx.voice_client.is_playing: 
        #     Music.queue.append(url)
        #     print(Music.queue)
        async with ctx.typing():
            player = await Music.YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            await ctx.respond('Now playing: {}'.format(player.title))
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    @slash_command(guild_ids=config["test_guild_id"], description="Changes the player's volume")
    async def volume(self, ctx, volume: int):

        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        if volume >= 1 and volume <= 200:
            ctx.voice_client.source.volume = volume / 100
            await ctx.respond("Changed volume to {}%".format(volume))
        else:
            await ctx.respond(f"Versuchs gar nicht erst du Hurensohn, dein IQ beträgt: {volume}")
            
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
    

def setup(bot):
    bot.add_cog(Music(bot))