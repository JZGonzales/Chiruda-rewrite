from discord.ext import commands
from typing import Optional

import discord

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_role = None


    async def is_mod(ctx):
        return ctx.author.top_role.permissions.manage_channels


    @commands.group()
    @commands.check(is_mod)
    async def set(self, ctx):
        roles = ctx.guild.roles

        for role in roles:
            if role.name == 'Chiruda-mute':
                self.mute_role = role
                skip = True

        if not skip:
            role = await ctx.guild.create_role(name='Chiruda-mute',
                                            reason='Chiruda mute role')
            self.mute_role = role


        if ctx.invoked_subcommand.name == 'jail':
            for channel in ctx.guild.channels:
                if channel.permissions_for(self.mute_role).send_messages:
                    await channel.set_permissions(self.mute_role,
                                                send_messages=False)


    @set.command()
    async def jail(self, ctx, channel:Optional[discord.TextChannel]=None):
        if channel == None:
            for channel in ctx.guild.channels:
                if channel.name == 'jail':
                    await channel.set_permissions(self.mute_role,
                                            send_messages=True
                    )
                    return
        
        
            await ctx.guild.create_text_channel(name='jail',
                        overwrites={
                        self.mute_role:discord.PermissionOverwrite(send_messages=True)
                        }
            ) # Crazy looking

        if type(channel) == discord.TextChannel:
            await channel.set_permissions(self.mute_role,
                                          send_messages=True)

            await ctx.send(f'Set {channel.mention} as the jail channel!', delete_after=5)

        
    @set.error
    async def set_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You are not permitted to use that command!')

def setup(bot):
    bot.add_cog(Moderation(bot))