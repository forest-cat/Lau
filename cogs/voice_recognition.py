import imp
from vosk import Model, KaldiRecognizer, SetLogLevel
from discord.commands import slash_command, Option 
from difflib import SequenceMatcher
from discord.ext import commands
import speech_recognition
import discord
import asyncio
import pyttsx3
import random
import wave
import json
import wave
import copy
import sys
import os

# Importing the read_config() function from bot.py file and music module
sys.path.append(os.path.dirname(__file__)[:-4])
from bot import read_config
#!from music import Music this needs a fix so the cog is loaded normal again (i probably have to change things with the folder and the sys append)



class Voice_Recognition(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stopped = True
        self.recognizer = speech_recognition.Recognizer()
        self.path = os.path.dirname(os.getcwd()) + r"\Lau\audio" # Changing into the bots root folder and then the audio folder
        self.current_guild = None


### FUNCTIONS ###

    async def recognize_voice(self, user_id, audio):
        os.chdir(self.path)
        #os.chdir(os.path.dirname(os.getcwd()) + r"\Lau\audio")
        # Converting from mp3 to wav
        with open(f"{user_id}.mp3", "wb") as file:
            file.write(audio.file.read())

        # Turns the file into an wave file from a mp3 file, due to problems with wave sink
        from pydub import AudioSegment
        sound = AudioSegment.from_mp3(f"{user_id}.mp3")
        sound.export(f"{user_id}.wav", format="wav")
        
        # Changes the audio channels from 2 (stereo) to 1 (mono) so the model can process it 
        sound = AudioSegment.from_wav(f"{user_id}.wav")
        sound = sound.set_channels(1)
        sound.export(f"{user_id}.wav", format="wav")

        # Opens the file again and starts analyzing the audio and initiating the voice model
        with wave.open(f"{user_id}.wav", "rb") as wf:
            model = Model(lang="en-us")
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            # Putting the audio chunks in the model
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if not rec.AcceptWaveform(data):
                    pass
                    
            json_final = json.loads(rec.PartialResult())
            print(self.current_guild)
            print(f"{json_final['partial']} [by {user_id}]")
            possible_commands = json_final['partial'].split()
            print(possible_commands)
            for command in possible_commands:
                if SequenceMatcher(None, command, "play").ratio() > 0.5:
                    print(f"playing music now by {user_id}")
            

            for channel in read_config()['bot_channels']:
                channel = self.bot.get_channel(channel)
                #await channel.send(f"{json_final['partial']} [by <@{user_id}>]")
        # if os.path.exists(f"{user_id}.mp3") and os.path.exists(f"{user_id}.wav"):
        #     os.remove(f"{user_id}.mp3")
        #     os.remove(f"{user_id}.wav")

    async def finished_callback(self, sink, ctx):
        #recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
        sink_local = sink
        sink = discord.sinks.MP3Sink()
        if not self.stopped:
            ctx.voice_client.start_recording(sink, self.finished_callback, ctx)
        
        for user_id, audio in sink_local.audio_data.items(): # iterating over all the users which have spoken in the voice recording
            await self.recognize_voice(user_id, audio)
    
    
    async def audio_recording_loop(self, ctx):
        sink = discord.sinks.MP3Sink()
        ctx.voice_client.start_recording(sink, self.finished_callback, ctx)
        while not self.stopped:
            await asyncio.sleep(3)
            ctx.voice_client.stop_recording() # after this the callback function is called

    async def cleanup(self):
        #cleans up all audio in audio folder
        os.chdir(self.path)
        for file in os.listdir():
            try:
                os.remove(f"{self.path}\\{file}")
            except Exception as ex:
                await asyncio.sleep(3)
                os.remove(f"{self.path}\\{file}")




            
### COMMANDS ###

    @slash_command(guild_ids=read_config()["guild_ids"], description="Starts recording")
    async def start_record(self, ctx):
        self.stopped = False
        self.current_guild = ctx.guild
        self.audio_recording_loop_task = self.bot.loop.create_task(self.audio_recording_loop(ctx=ctx))
        await ctx.respond("started", ephemeral=True)
        


    @slash_command(guild_ids=read_config()["guild_ids"], description="Stops recording")
    async def stop_record(self, ctx):
        self.stopped = True
        self.audio_recording_loop_task.cancel()
        try:
            ctx.voice_client.stop_recording()
            await ctx.respond("stopped", ephemeral=True)
        except discord.sinks.errors.RecordingException:
            await ctx.respond("not recording currently", ephemeral=True)
        await self.cleanup()

           

    @start_record.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                ctx.voice_client.stop()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
    

### EVENTS ###
    
    # Disables logs from the vosk model
    @commands.Cog.listener()
    async def on_ready(self):
        SetLogLevel(-1)
    
def setup(bot):
    bot.add_cog(Voice_Recognition(bot))

    