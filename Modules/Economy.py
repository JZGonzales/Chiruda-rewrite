import datetime
import random
import json
import discord

from typing import Optional
from discord.ui import Button, View, Select
from discord.ext import commands
from .User_stats.stat_handler import user_stats

us = user_stats()
COIN = '<a:ccoin:958881860547665960>'
COLOR = 0xFD6C6B
SEP = '\u2800'

def __ap__(name):
    if name[-1] == 's':
        ap = '\''
    else:
        ap = '\'s'
    return ap


class Money(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command(description='Claims your daily free coins')
    async def daily(self, ctx):
        stats = us.get_stats(ctx.author)
        daily = stats.get('next_daily')
        coins = stats.get('coins')

        try:
            if datetime.datetime.fromisoformat(daily) > datetime.datetime.now(datetime.timezone.utc):
                time = datetime.datetime.fromisoformat(daily) - datetime.datetime.now(datetime.timezone.utc)
                hours, minutes, seconds = str(time).split(':')

                if hours != '0':
                    await ctx.send(f'You can get your next daily in {hours} hours and {minutes} minutes!')
                    return
                else:
                    await ctx.send(f'You can get your next daily in {minutes} minutes and {seconds[0:2]} seconds!')
                    return

        except:
            pass

        now = datetime.datetime.now(datetime.timezone.utc)
        time = now + datetime.timedelta(days=1)
        next_daily = time.isoformat()

        us.update_stats(ctx.author, coins=coins+200, next_daily=next_daily)

        embed = discord.Embed(title='Daily claimed!',
                              description=f'+{COIN}200',
                              timestamp=time,
                              color=COLOR)
        embed.set_footer(text=f'Come back to claim your daily tomorrow', icon_url=embed.Empty)
        
        await ctx.send(embed=embed)


    @commands.command(aliases=['money', 'coins'],
                      description='See how many coins you have')
    async def wallet(self, ctx):
        stats = us.get_stats(ctx.author)
        coins = stats.get('coins')

        embed = discord.Embed(title=f'{ctx.author.name}{__ap__(ctx.author.name)} wallet',
                              description=f'{COIN}{coins:,} coins',
                              color=COLOR)

        await ctx.send(embed=embed)


class Gambling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Try your luck and gamble your money away!')
    @commands.cooldown(1, 3)
    async def gamble(self, ctx, bet:Optional[int]=50):
        coins = us.get_stats(ctx.author).get('coins')

        if coins < bet:
            await ctx.send('You don\'t have enough credits', delete_after=5)
            return
        
        us.update_stats(ctx.author, coins=coins-bet)
        rng = random.randrange(0, 500)
        if rng == bet:
            winnings = bet*5
        elif rng in range(bet-5, bet+6):
            winnings = bet*1.7
        elif rng in range(bet-10, bet+11):
            winnings = bet*1.5
        elif rng in range(bet-15, bet+16):
            winnings = bet*1.2
        else:
            us.update_stats(ctx.author, coins=coins-bet)
            await ctx.send(f'You gambled {COIN}**{bet} coins** and lost it all')
            return
        
        winnings = int(winnings)
        us.update_stats(ctx.author, coins=coins+winnings)
        await ctx.send(f'You gambled {COIN}**{bet} coins** and won {COIN}**{winnings} coins**')


class Fishing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(description='Fish for items')
    @commands.cooldown(1, 3)
    async def fish(self, ctx):
        if ctx.invoked_subcommand == None:
            stats = us.get_stats(ctx.author)

            if stats.get('coins') < 5:
                await ctx.send('You don\'t have enough coins to fish!', delete_after=5)
                return

            WEIGHTS = {0:90, 1:50, 2:25, 3:8}
            RARITY = {0:'trash', 1:'common', 2:'uncommon', 3:'rare'}
            FISH = {
                'a boot':0, 'seaweed':0, 'water':0, 'a scuba diver':0,  'a grenade':0, 
                'a pair of crocs':0,'a garden gnome':1,  'a tadpole':1, 'fish sticks':1, 
                'a cod':1, 'a trout':1, 'a salmon':1, 'a burrito':1, 'a lobster':1, 
                'corn nuts':1, 'a catfish':2, 'a frog':2, 'a bass':2, 'a pollock':2, 
                'a couple dollars':2, 'a shark':3, 'a solid gold fish':3, 'a rolex':3
            }

            # weights creates a list of probabilities corresponding to
            # to each item in the list of fish
            random_fish = random.choices(
                list(FISH),
                weights=[WEIGHTS.get(w) for w in list(FISH.values())],
                k=1
            )
            random_fish = random_fish[0]

            current = stats.get(f'fish_{RARITY.get(FISH.get(random_fish))}')
            kwargs = {
                f'fish_{RARITY.get(FISH.get(random_fish))}':current+1,
                'coins':stats.get('coins')-5
            }
            us.update_stats(ctx.author, **kwargs)

            embed = discord.Embed(description=f'You caught **{random_fish} ({RARITY.get(FISH.get(random_fish))}**)\n'
                                              f'You paid {COIN}5 for casting',
                                  color=COLOR)
            await ctx.send(embed=embed)

    
    @fish.command(aliases=['inv'],
                  description='See how many fish you\'ve caight')
    async def inventory(self, ctx):
        stats = us.get_stats(ctx.author)
        sell_amount = {
            'trash':3,
            'common':5,
            'uncommon':10,
            'rare':50
        }
        inventory = {
            'trash':stats.get('fish_trash'),
            'common':stats.get('fish_common'),
            'uncommon':stats.get('fish_uncommon'),
            'rare':stats.get('fish_rare')
        }
        field_name = []
        field_value = []
        for fish, amount in zip(list(inventory), list(inventory.values())):
            field_name.append(fish.title())
            fish_value = sell_amount.get(fish)*amount
            field_value.append(f'> Held: {amount}\n> Value: {fish_value}')

        embed = discord.Embed(
            title=f'{ctx.author.name}{__ap__(ctx.author.name)} inventory',
            color=COLOR)
            
        for i in range(len(field_name)):
            embed.add_field(name=field_name[i], value=field_value[i], inline=False)

        await ctx.send(embed=embed)

    
    @fish.command(description='Sell your fish')
    async def sell(self, ctx, fish_type):
        stats = us.get_stats(ctx.author)
        coins = stats.get('coins')
        sell_amount = {
            'fish_trash':3,
            'fish_common':5,
            'fish_uncommon':10,
            'fish_rare':50
        }
        amnt_of_fish = stats.get(f'fish_{fish_type}')

        if amnt_of_fish == None:
            await ctx.send('Invalid fish type!', delete_after=5)
            return
        if amnt_of_fish == 0:
            await ctx.send('You don\'t have any of that fish to sell!', delete_after=5)
            return

        total_coins = sell_amount.get(f'fish_{fish_type}')*amnt_of_fish
        confirmation = await ctx.send(f'Are you sure you want to sell {amnt_of_fish} {fish_type} for {total_coins}?\nreply with \'y\' to confirm.', delete_after=15)
        
        def check(m):
            return (m.content == 'y' and
                    m.channel == ctx.channel and
                    m.author == ctx.author and
                    ctx.bot.get_message(confirmation.id) != None)

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=15)
        except:
            return

        await msg.delete()
        await confirmation.delete()
        kwargs = {
            'coins':coins+total_coins,
            f'fish_{fish_type}':0
        }
        us.update_stats(
            ctx.author,
            **kwargs
        )
        embed = discord.Embed(
            title='Fish sold!', 
            description=f'-{amnt_of_fish} {fish_type}\n+ {COIN}{total_coins}',
            color=COLOR
        )
        await ctx.send(embed=embed)


    @fish.error
    async def fish_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Please slow down!!', delete_after=3)


def setup(bot):
    bot.add_cog(Money(bot))
    bot.add_cog(Gambling(bot))
    bot.add_cog(Fishing(bot))
