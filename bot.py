from discord.ext import commands
import discord
import json
import os

os.chdir(os.path.dirname(__file__))
# Reading Config File
with open("config.json", "r") as config:
    config = json.load(config)

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


# Loading the Extensions aka. cogs
registered_extensions = ['cogs.music', 'cogs.r6tracker', 'cogs.slash', 'cogs.twitch']

for extension in registered_extensions:
    bot.load_extension(extension)
    print(f"\033[92m[+]\033[00m loaded: {extension}")


# Running the actual bot
@bot.event
async def on_ready():
    print(f"Logged in as: \033[36m{bot.user.name}\033[90m#\033[37m{bot.user.discriminator}\033[0m")


# An Example for a slash command
# @bot.slash_command(guild_ids=TESTING_GUILD_ID)  # create a slash command for the supplied guilds
# async def hellofrommain(ctx):
#     """Say hello to the bot"""  # the command description can be supplied as the docstring
#     await ctx.respond(f"Hello {ctx.author}!")


bot.run(TOKEN)