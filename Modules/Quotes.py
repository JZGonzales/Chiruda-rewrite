from .Quotes_cache.quote_handler import quote_handler
from discord.ext import commands, pages
from typing import Union

import discord
import asyncio
import random
import math


class Quotes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def all_quotes(self, quotes):
        quote_pages = []

        embeds = [discord.Embed(title='Quotes for this server') for i in range(math.ceil(len(quotes)/5))]
        embed_num = 0
        for embed in embeds:
            for quote in quotes[embed_num:embed_num+5]:
                embed.add_field(name=quote.get('Author'),
                                value=f"{quote.get('Quote')} [{quote.get('Index')}]",
                                inline=False)
            embed_num += 5
            quote_pages.append(embed)

        return quote_pages


    @commands.group(aliases=['q', 'quote'],
                    description='Shows all quotes or show a quote by the index')
    async def quotes(self, ctx, index:Union[int, str]=None):
        if ctx.invoked_subcommand == None:
            quotes = quote_handler(ctx.guild.id).get_quotes()
            if index != None:
                embed = discord.Embed(title=f'Quote #{index}')
                embed.add_field(name=quotes[index-1].get('Author'),
                                value=quotes[index].get('Quote'),
                                inline=False)

            paginator = pages.Paginator(pages=self.all_quotes(quotes),
                                        loop_pages=True)
            await paginator.send(ctx)
            return


    @quotes.command(description='Adds a quote to the server')
    async def add(self, ctx,
                  author: commands.clean_content,
                  *, quote):
        if author.startswith('@'):
            author = author[1:]
        quote_handler(ctx.guild.id).add_quote(author, quote)
        await ctx.send('Quote added!', delete_after=5)

    @quotes.command(description='Removes a quote from the server')
    async def remove(self, ctx, index):
        msg = await ctx.send('Are you sure?')
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')

        def check(reaction, user):
            return (user == ctx.author and str(reaction.emoji) == '👍' or 
                   user == ctx.author and str(reaction.emoji) == '👎')
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '👍':
                quote_handler(ctx.guild.id).remove_quote(index)
                await msg.delete()
                await ctx.send('Quote deleted!', delete_after=5.0)
            elif str(reaction.emoji) == '👎':
                await msg.delete()
                await ctx.send('Cancelled!', delete_after=5)
                return
            else:
                return
        except asyncio.TimeoutError:
            await msg.delete()
            return
            

def setup(bot):
    bot.add_cog(Quotes(bot))