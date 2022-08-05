from discord.commands import slash_command, Option 
from discord.ext import commands
import discord

TESTING_GUILD_ID = [831978811435515944]

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @slash_command(guild_ids=TESTING_GUILD_ID)  # Create a slash command for the supplied guilds.
    async def addvote(self, ctx):
        """Adds an Up and Downvote Rection to the last message in the Channel"""
        messages = await ctx.channel.history(limit=1).flatten()
        await messages[0].add_reaction("<:upvote:1005110315022827610>")
        await messages[0].add_reaction("<:downvote:1005110312812433439>")
        await ctx.respond(f"Added to Reactions to: `{messages[0].content}`", ephemeral=True)




def setup(bot):
    bot.add_cog(Slash(bot))

    