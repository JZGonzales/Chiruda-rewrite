from discord.ext import commands

class Osu(commands.Cog):
    pass

def setup(bot):
    bot.add_cog(Osu(bot))