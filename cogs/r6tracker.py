from discord.commands import slash_command, Option 
from requests_html import AsyncHTMLSession
from discord.ext import commands
import discord
import json
import os



class R6Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    os.chdir(os.path.dirname(__file__))

    with open("../config.json", "r") as config:
        config = json.load(config)

    async def get(self):
        session = AsyncHTMLSession()
        page1 = await session.get("https://r6.tracker.network/profile/pc/BurakDasBoereck")
        await page1.html.arender(timeout=6000)
        print("531" in page1.text)

    # https://r6.tracker.network/profile/pc/BurakDasBoereck
    @slash_command(guild_ids=config["test_guild_id"])
    async def stats(self, ctx, device: Option(str, "Choose a Device", choices=["PC", "PlayStation", "XBox", "Toaster"]), username: str):
        """Gets the Rainbow Six stats for the given Player"""
        await ctx.respond(f"{username} is playing on {device}")
        await self.get()
        
        

def setup(bot):
    bot.add_cog(R6Tracker(bot))
