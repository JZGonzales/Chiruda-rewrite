from discord.ext import commands
from discord import utils
from datetime import datetime
import discord


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.disconnect = None

    @commands.Cog.listener()
    async def on_resumed(self):
        dc_time = datetime.utcnow() - self.disconnect
        print(f"Session reconnect on {datetime.now().strftime('%A, %d-%m-%Y at %I:%M:%S %p')}",
              f"\nDisconnected for {dc_time} seconds")
        self.disconnect = None


    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f"Session disconnect on {datetime.now().strftime('%A, %d-%m-%Y at %I:%M:%S %p')}")
        self.disconnect = datetime.utcnow()

def setup(bot):
    bot.add_cog(events(bot))