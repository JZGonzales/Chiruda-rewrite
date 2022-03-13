from .Helpers.Embeds import make_embed
from discord.ext import commands
from typing import Tuple

import discord
import asyncio


class Reactions(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

        # Listener attributes
        self.pairs = []
        self.message = None


    @commands.command(aliases=['rr'])
    async def reactrole(
        self, ctx,
        roles: commands.Greedy[discord.Role],
        *emotes
        ):

        fields = []
        for role, emote in zip(roles, emotes):
            field = ['\u200b', f'React with {emote} for <@&{role.id}>', False]
            fields.append(field)
            self.pairs.append({'Emote':emote, 'Role':role})

        embed = make_embed(
            title='React Roles',
            description=None,
            fields=fields,
            color=0xFF696B
        )

        ask_for_desc = await ctx.send(
            'Send a message for the description or react with 👎 to skip'
        )
        await ask_for_desc.add_reaction('👎')

        def check_message(message):
            return message.author == ctx.author

        def check_react(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '👎'

        done, _ = await asyncio.wait([
                    self.bot.wait_for('message', check=check_message),
                    self.bot.wait_for('reaction_add', check=check_react)
                ], return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if type(task.result()) == discord.Message:
                embed.description = task.result().content
                await task.result().delete()
                await ask_for_desc.delete()
            else:
                await ask_for_desc.delete()

        msg = await ctx.send(embed=embed)
        self.message = msg

        for emote in emotes:
            await msg.add_reaction(emote)

        await ctx.message.delete()
        

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            if self.message == None:
                return

            if payload.message_id == self.message.id:
                for reaction in self.pairs:
                    new_reaction = reaction.get('Emote')
                    if new_reaction == str(payload.emoji):
                        await payload.member.add_roles(reaction.get('Role'))


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id != self.bot.user.id:
            if payload.message_id == self.message.id:
                for reaction in self.pairs:
                    new_reaction = reaction.get('Emote')
                    if new_reaction == str(payload.emoji):
                        guild = self.bot.get_guild(payload.guild_id)
                        member = guild.get_member(payload.user_id)
                        await member.remove_roles(reaction.get('Role'))

def setup(bot):
    bot.add_cog(Reactions(bot))