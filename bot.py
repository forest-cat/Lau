from shutil import ExecError
from discord.commands import slash_command
from discord.ext import commands
import discord
import json
import os


def read_config():
    os.chdir(os.path.dirname(__file__))
    # Reading Config File
    with open("config.json", "r") as config:
        config = json.load(config)
    return config


config = read_config()

# Defining all variables
PREFIX = "%"
TESTING_GUILD_ID = config["guild_ids"]
TOKEN = config["token"]
DESCRIPTION = """This is a simple Bot which can play music, access the r6tracker networks database, administrate your server and much much more..... """
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.presences = True


bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION, intents=INTENTS)
bot.remove_command('help')


# Loading the Extensions aka. cogs
registered_extensions = ['cogs.main', 'cogs.music', 'cogs.r6tracker', 'cogs.slash', 'cogs.twitch']

for extension in registered_extensions:
    bot.load_extension(extension)
    print(f"\033[92m[+]\033[00m Extension loaded: {extension}")

@commands.has_permissions(administrator=True)
@bot.slash_command(guild_ids=config["guild_ids"], description="Loads the gives cog")
async def load_cog(ctx, cog_name: str):
    bot.load_extension(cog_name)
    await ctx.respond(f"The Cog: `{cog_name}` has been loaded", ephemeral=True)

@commands.has_permissions(administrator=True)
@bot.slash_command(guild_ids=config["guild_ids"], description="Unloads the gives cog")
async def unload_cog(ctx, cog_name: str):
    try:
        bot.unload_extension(cog_name)
        await ctx.respond(f"The Cog: `{cog_name}` has been unloaded", ephemeral=True)
    except discord.errors.ExtensionNotLoaded:
        await ctx.respond(f"The Cog: `{cog_name}` was never loaded", ephemeral=True)
    

bot.run(TOKEN)