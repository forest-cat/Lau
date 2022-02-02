from discord.commands import slash_command, Option 
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

    # https://r6.tracker.network/profile/pc/BurakDasBoereck
    @slash_command(guild_ids=config["test_guild_id"])
    async def stats(self, ctx, device: Option(str, "Choose the Device", choices=["PC", "PlayStation", "XBox"]), username: str):
        """Says hello from the Cog"""
        await ctx.respond(f"{username} is playing on {device}")
        

def setup(bot):
    bot.add_cog(R6Tracker(bot))
