from discord.commands import slash_command, Option 
from requests_html import AsyncHTMLSession
from discord.ext import commands
from bs4 import BeautifulSoup
import discord
import json
import os



class R6Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    os.chdir(os.path.dirname(__file__))

    
    # Deklaring vars
    page = None
    username = None
    profile_link = None
    level = None
    mains = None

    with open("../config.json", "r") as config:
        config = json.load(config)

    async def get(self):
        session = AsyncHTMLSession()
        page1 = await session.get("https://r6.tracker.network/profile/pc/BurakDasBoereck")
        await page1.html.arender(timeout=6000)
        self.page = page1
        self.profile_link = self.page.html.xpath('/html/body/div[4]/div[2]/div[1]/div/div[1]/div/img')[0].attrs['src']
        soup = BeautifulSoup(self.page.content, 'html.parser')
        print(soup.find_all(class_="trn-defstat__value-stylized"))
        #self.level = self.page.html.xpath('/html/body/div[4]/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[1]/div/div[2]')[0].text
        #self.mains = [self.page.html.xpath('/html/body/div[4]/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[2]/img[1]')[0].attrs['title'], self.page.html.xpath('/html/body/div[4]/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[2]/img[2]')[0].attrs['title'], self.page.html.xpath('/html/body/div[4]/div[2]/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[2]/img[3]')[0].attrs['title']]
        print(self.mains)
    
    def build_embed(self):
        EmbedStats = discord.Embed(colour=discord.Color.orange(), title=f"Stats from {self.username}")
        EmbedStats.set_thumbnail(url=self.profile_link)
        #EmbedStats.add_field(inline=False, name="General", value=f"Level: {self.level}\nMains: {self.mains[0]} {self.mains[1]} {self.mains[2]}")
        return EmbedStats

    # https://r6.tracker.network/profile/pc/BurakDasBoereck
    @slash_command(guild_ids=config["test_guild_id"])
    async def stats(self, ctx, device: Option(str, "Choose a Device", choices=["PC", "PlayStation", "XBox"]), username: str):
        """Gets the Rainbow Six stats for the given Player"""
        self.username = username
        msg = await ctx.respond(f"`Looking up the stats for {username}`")
        async with ctx.typing():
            await self.get()
            await msg.edit_original_message(content=f"`Found Stats for {self.username}`", embed=self.build_embed())
        
        
        

def setup(bot):
    bot.add_cog(R6Tracker(bot))
