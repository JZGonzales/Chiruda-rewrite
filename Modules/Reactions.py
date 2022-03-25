from discord.ext import commands

import discord
import asyncio


class React(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.author = None
        self.message = None
        self.embed = None
        self.pairs = []


    async def is_manager(ctx):
        return ctx.author.top_role.permissions.manage_guild

    
    @commands.check(is_manager)
    @commands.command(aliases=['rr'],
                      description='Sets up a reactrole message. Must have the \'Manage Server\' permission to use')
    async def reactrole(self, ctx, *roles: discord.Role):
        for role in roles:
            if ctx.guild.get_member(self.bot.user.id).top_role < role:
                await ctx.send('One or more of these roles is not assignable. Please change the role hierarchy so your roles are below the bot role!')
                return
            self.pairs.append({'Emote':None, 'Role':role})
        embed = discord.Embed(title='React roles!')
        embed.add_field(name='Roles',
                        value='\n'.join([role.name for role in roles]),
                        inline=False)

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
        self.author = ctx.author
        self.embed = embed


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id != self.bot.user.id:
            if user.id == self.author.id and self.message.id == reaction.message.id:
                roles = self.embed.fields[0].value.splitlines()
                index = [emote.emoji for emote in reaction.message.reactions].index(reaction.emoji)

                try:
                    display_role = roles.pop(index)
                except IndexError:
                    await reaction.message.remove_reaction(reaction, user)
                    return

                roles.insert(index, f'{display_role} : {reaction.emoji}')
                
                self.pairs[index].update({'Emote':reaction.emoji})

                embed = self.embed
                embed.set_footer(text='React for any of these roles!', icon_url=discord.Embed.Empty)
                embed.set_field_at(0, name=embed.fields[0].name,
                                    value='\n'.join([role for role in roles]),
                                    inline=False)

                await reaction.message.edit(embed=embed)
                return

            for pair in self.pairs:
                match_emote = pair.get('Emote')
                if match_emote == reaction.emoji:
                    await user.add_roles(pair.get('Role'))


def setup(bot):
    bot.add_cog(React(bot))