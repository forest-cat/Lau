from discord.ext import commands
import discord

# Defining all variables
PREFIX = "%"
TESTING_GUILD_ID = [831978811435515944]
TOKEN = ""
DESCRIPTION = """This is a simple Bot which can play music, access the r6tracker networks database, administrate your server and much much more..... """


bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION)


# Loading the Extensions aka. cogs
registered_extensions = ['cogs.music', 'cogs.slash']

for extension in registered_extensions:
    bot.load_extension(extension)
    print(f"[+] loaded: {extension}")


# Running the actual bot
@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user.name}")

@bot.slash_command(guild_ids=TESTING_GUILD_ID)  # create a slash command for the supplied guilds
async def hellofrommain(ctx):
    """Say hello to the bot"""  # the command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")


bot.run(TOKEN)