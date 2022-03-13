from .Quotes_cache.quote_handler import quote_handler
from .Helpers.Embeds import make_embed
from discord.ui import Button, View
from discord.ext import commands

import discord
import asyncio
import random
import math


class Quotes(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.page = 1


    @commands.command(aliases=['aq'])
    async def add_quote(self, 
                        ctx, 
                        author: commands.clean_content, 
                        *, quote
                    ):
        if author.startswith('@'):
            author = author[1:]
        quote_handler(ctx.guild.id).add_quote(author, quote)
        await ctx.send('Quote added!', delete_after=5)


    @commands.command(aliases=['rq'])
    async def remove_quote(self, ctx, index):
        msg = await ctx.send('Are you sure?')
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0)
            if user.id == ctx.author.id and str(reaction.emoji) == '👍':
                quote_handler(ctx.guild.id).remove_quote(index)
                await msg.delete(delay=5.0)
                await ctx.send('Quote deleted!', delete_after=5.0)

            elif user.id == ctx.author.id and str(reaction.emoji) == '👎':
                await msg.delete(delay=5.0)
                await ctx.send('Cancelled!', delete_after=5.0)
        
        except asyncio.TimeoutError:
            await msg.delete()
            return


    @commands.command(aliases=['q'])
    async def quotes(self, ctx, index=None):
        quotes = quote_handler(ctx.guild.id).get_quotes()
        server_name = ctx.guild.name

        async def button_press(interaction):
            if interaction.data['custom_id'] == 'Next':
                self.page += 1
                if self.page > int(math.ceil(len(quotes)/5)):
                    return
            
            if interaction.data['custom_id'] == 'Previous':
                self.page -= 1
                if self.page == 0:
                    return

            global embed
            global embed_fields

            embed.clear_fields()
            embed.remove_footer()

            for field in embed_fields[self.page*5-5:self.page*5]:
                embed.add_field(name=field[0], value=field[1], inline=False)

            embed.set_footer(
                text=f'Page {self.page}/{int(math.ceil(len(quotes)/5))} ({len(quotes)})', 
                icon_url=discord.Embed.Empty
                )
            
            await interaction.response.edit_message(embed=embed)

        global embed_fields
        embed_fields = []
        for quote in quotes:
            info = [quote['Author'], f"{quote['Quote']} [{quote['Index']}]", False]
            embed_fields.append(info)

        if index == None:
            v = View()
            prev = Button(
                style=discord.ButtonStyle.primary,
                custom_id='Previous',
                label='Previous'
                )
            next_ = Button(
                style=discord.ButtonStyle.primary,
                custom_id='Next',
                label='Next'
                )
            v.add_item(prev)
            v.add_item(next_)
            next_.callback, prev.callback = button_press, button_press

            embed_fields = embed_fields[self.page*5-5:self.page*5]

        if index != None:
            try:
                index = int(index)
                embed_fields = [embed_fields[index-1]]
            
            except ValueError:
                index = index.lower()
                choices = []
                for quote in embed_fields:
                    if quote[0].lower() == index:
                        choices.append(quote)

                embed_fields = [random.choice(choices)]

        global embed
        embed = make_embed(
            title=f"Quotes for {server_name}",
            fields=embed_fields,
            footer=[f'Page {self.page}/{int(math.ceil(len(quotes)/5))} ({len(quotes)})', discord.Embed.Empty],
            color=0xFF696B
        )
        try:
            await ctx.send(embed=embed, view=v)
        except UnboundLocalError:
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Quotes(bot))