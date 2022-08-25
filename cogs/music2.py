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
            self.config = json.load(config)

    