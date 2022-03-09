from discord.ext import commands
from datetime import datetime
import random


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        a = datetime.utcnow()
        b = ctx.message.created_at
        b = b.replace(tzinfo=None) - b.utcoffset()
        c = a - b
        await ctx.send(f'Pong! ({abs(round(c.total_seconds()*1000))}ms)')

    @commands.command(aliases=['cf'])
    async def coinflip(self, ctx):
        coin = random.randrange(0, 2)
        if coin == 0:
            await ctx.send('Heads!')
        else:
            await ctx.send('Tails!')

def setup(bot):
    bot.add_cog(General(bot))