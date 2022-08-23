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
        await ctx.respond(f"Added to Reactions to: `{messages[0].content}`", ephemeral=True)
    
    @slash_command(guild_ids=config["guild_ids"], description="Let the universe decide")
    async def coinflip(self, ctx):
        await ctx.respond(f"The universe has made a decision, the coin landed on: `{'Tails' if random.randint(0,1) == 1 else 'Heads'}`")
    
    @slash_command(guild_ids=config["guild_ids"], description="Find your lucky number now")
    async def randomnumber(self, ctx, min: int, max: int):
        await ctx.respond(f"Your lucky number today is: `{random.randint(min, max) if max >= min else '∞'}`")
    





def setup(bot):
    bot.add_cog(Slash(bot))

    