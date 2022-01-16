from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.channel.send("Hello")
    






def setup(bot):
    bot.add_cog(Music(bot))