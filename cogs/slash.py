from discord.commands import slash_command, Option 
from discord.ext import commands
import discord

TESTING_GUILD_ID = [831978811435515944]

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_command(guild_ids=TESTING_GUILD_ID)  # Create a slash command for the supplied guilds.
    async def hellofromcog(self, ctx):
        """Says hello from the Cog"""
        await ctx.respond("Hi, this is a slash command from a cog!")




def setup(bot):
    bot.add_cog(Slash(bot))

    