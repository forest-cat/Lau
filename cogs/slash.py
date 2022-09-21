from discord.commands import slash_command, Option 
from discord.ext import commands
import discord
import random
import json
import os


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    os.chdir(os.path.dirname(__file__))

    with open("../config.json", "r") as config:
        config = json.load(config)
    
    @slash_command(guild_ids=config["guild_ids"], description="Adds an Up and Downvote Rection to the last message in the Channel")
    async def addvote(self, ctx):
        messages = await ctx.channel.history(limit=1).flatten()
        await messages[0].add_reaction("<:upvote:1005110315022827610>")
        await messages[0].add_reaction("<:downvote:1005110312812433439>")
        await ctx.respond(f"Added to Reactions to: `{messages[0].content[:1800]}`", ephemeral=True)
    
    @slash_command(guild_ids=config["guild_ids"], description="Let the universe decide")
    async def coinflip(self, ctx):
        await ctx.respond(f"The universe has made a decision, the coin landed on: `{'Tails' if random.randint(0,1) == 1 else 'Heads'}`")
    
    @slash_command(guild_ids=config["guild_ids"], description="Find your lucky number now (default range is 1-100)")
    async def randomnumber(self, ctx, min: int = 1, max: int = 100):
        await ctx.respond(f"Your lucky number today is: `{random.randint(min, max) if max >= min else '∞'}`")
    
    @slash_command(guild_ids=config["guild_ids"], description="Shows you the bots latency to the Discord API")
    async def ping(self, ctx):
        await ctx.respond(f"My Latency is: `{int(round(self.bot.latency*60, 0))}`ms")

    @slash_command(guild_ids=config["guild_ids"], description="Calculates the time simon needs to show up, given the time simon said he would need")
    async def simon_time(self, ctx, minutes: int):
        await ctx.respond(f"The time simon will need is: `{int(round(minutes * random.uniform(1,4), 0))}`min")
    
def setup(bot):
    bot.add_cog(Slash(bot))

    