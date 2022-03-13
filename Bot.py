from discord.ext import commands
from MY_TOKEN import token

import datetime
import discord
import pathlib
import asyncio
import os


desc = None # Bot description
intents = discord.Intents.default()
intents.members = True #Enables changing server member things
intents.reactions = True
bot = commands.Bot(command_prefix='~', description=desc, intents=intents)

# Stolen from stackoverflow like a good programmer :)
async def load_cogs():
    loaded_cogs = []
    for filename in os.listdir('./Modules'):
        if filename.endswith('.py'):
            bot.load_extension(f'Modules.{filename[:-3]}')
            loaded_cogs.append(f'Modules.{filename[:-3]}')
    
    return loaded_cogs


@bot.command(aliases=['rl'])
async def reload_cogs(ctx, cog):
    if await bot.is_owner(ctx.author):
        cog = cog.title()
        try:
            bot.reload_extension(f'Modules.{cog}')
            await ctx.send(f"Successfully reloaded {cog}")
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f'There was an error reloading {cog}')
    else:
        await ctx.send('You are not the bot owner!')
    

@bot.event
async def on_ready():
    try:
        print(f"Succefully loaded {await load_cogs()}")
    except discord.errors.ExtensionAlreadyLoaded:
        pass


@bot.event
async def on_resumed():
    print(f'Session resumed on {datetime.datetime.now()}')


@bot.event
async def on_connect():
    _status = discord.Game('with errors')
    await bot.change_presence(status=discord.Status.dnd, activity=_status)
    print(f'Logged in as {bot.user} (ID <#{bot.user.id}>)')


@bot.event
async def on_disconnect():
    print(f'Disconnect occured on {datetime.datetime.now()}')


bot.run(token)