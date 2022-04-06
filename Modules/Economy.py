from .User_stats.stats_handler import edit_stats
from discord.ext import commands
from math import sqrt

import datetime
import discord
import random

user_stats = edit_stats()

class Farming(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.coin = '<a:ccoin:958881860547665960>'

    def get_level(self, xp):
        return abs(round(((xp-1)/2)**.57142))

    def determine_money(self, num):
        if num >= 10 and num <= 90:
            s_num = str(num)
            num = int(s_num[0])*2
            return num

        elif num < 10:
            return 0

        elif num > 90:
            return 35


    @commands.command()
    async def plant(self, ctx):
        stats = user_stats.get(ctx.author.id)

        if stats.get('planted'):
            await ctx.send('You can\'t plant more until you harvest first!', delete_after=5)
            return

        try:
            if datetime.datetime.fromisoformat(stats.get('harvest')) > datetime.datetime.now(datetime.timezone.utc):
                await ctx.send('You can\'t plant yet!', delete_after=5)
                return
        except:
            pass

        user_stats.update(ctx.author.id, cyield=random.randrange(0, 100))
        xp = stats.get('xp')
        level = stats.get('level')
        if level <= 2:
            xp_upper_limit = 5
        else:
            xp_upper_limit = round(sqrt(level)+1)
        
        new_xp = random.randrange(1, xp_upper_limit)

        level_up = False
        xp_level = self.get_level(xp)
        if xp_level > level:
            level = xp_level
            level_up = True

        #date stuff
        now = datetime.datetime.now(datetime.timezone.utc)
        m = 30
        time = now + datetime.timedelta(minutes=m)
        harvest = time.isoformat()

        user_stats.update(ctx.author.id, xp=new_xp+xp, level=level, planted=True, harvest=harvest)

        if level_up:
            gains = f"+{new_xp}XP\n+1 Level (Level {level})"
        else:
            gains = f"+{new_xp}XP"

        embed = discord.Embed(title='Crops planted!',
                              color=0xFD6C6B)
        embed.add_field(name='You gained',
                        value=gains,
                        inline=False)
        embed.set_footer(text='You can harvest in 30 minutes',
                        icon_url=discord.Embed.Empty)
        
        await ctx.send(embed=embed)

    
    @commands.command()
    async def harvest(self, ctx):
        stats = user_stats.get(ctx.author.id)
        player_money = stats.get('money')
        player_xp = stats.get('xp')
        player_level = stats.get('level')
        harvest_time = stats.get('harvest')

        if not stats.get('planted'):
            await ctx.send('You can\'t harvest until you plant!', delete_after=5)
            return

        try:
            if datetime.datetime.fromisoformat(harvest_time) > datetime.datetime.now(datetime.timezone.utc):
                time_left = datetime.datetime.fromisoformat(harvest_time) - datetime.datetime.now(datetime.timezone.utc)
                _, minutes, seconds = str(time_left).split(':')
                if minutes == '0':
                    await ctx.send(f'You can harvest in {seconds[:2]} seconds!', delete_after=10)
                else:
                    await ctx.send(f'You can harvest in {minutes} minutes and {seconds[:2]} seconds!', delete_after=10)
                return
        except:
            pass

        money = self.determine_money(stats.get('yield'))
        xp_level = self.get_level(player_xp)

        if money == 35:
            user_stats.update(ctx.author.id, money=player_money+money, xp=player_xp+10, planted=False)
            if xp_level > player_level:
                user_stats.update(ctx.author.id, level=xp_level, planted=False)
                gains = f'+{self.coin}{money}\n+10XP\n+1 Level (Level {xp_level})'
            
            else:
                gains = f'+{self.coin}{money}\n+10XP'

        elif money == 0:
            user_stats.update(ctx.author.id, planted=False)
            gains = f'+{self.coin}0'

        else:
            user_stats.update(ctx.author.id, money=player_money+money, planted=False)
            gains = f'+{self.coin}{money}'

        embed = discord.Embed(title='Crops harvested!',
                              color=0xFD6C6B)
        embed.add_field(name='You gained',
                        value=gains,
                        inline=False)
        embed.set_footer(text='Use ~plant to plant more crops!',
                         icon_url=discord.Embed.Empty)

        await ctx.send(embed=embed)


class Gambling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.coin = '<a:ccoin:958881860547665960>'

    @commands.command()
    async def daily(self, ctx):
        stats = user_stats.get(ctx.author.id)
        money = stats.get('money')
        next_daily = stats.get('daily')

        try:
            if datetime.datetime.fromisoformat(next_daily) > datetime.datetime.now(datetime.timezone.utc):
                time = datetime.datetime.fromisoformat(next_daily) - datetime.datetime.now(datetime.timezone.utc)
                hours, minutes, seconds = str(time).split(':')

                if hours != '0':
                    await ctx.send(f'You can get your next daily in {hours} hours and {minutes} minutes!')
                    return
                else:
                    await ctx.send(f'You can get your next daily in {minutes} minutes and {seconds[0:2]} seconds!')
                    return

        except Exception as e:
            print(e)
            pass

        now = datetime.datetime.now(datetime.timezone.utc)
        time = now + datetime.timedelta(days=1)
        daily = time.isoformat()

        user_stats.update(ctx.author.id, money=money+200, daily=daily)

        embed = discord.Embed(title='Daily claimed!',
                              color=0xFD6C6B)
        embed.add_field(name='You gained',
                        value=f'+{self.coin}200')
        
        await ctx.send(embed=embed)

    
    @commands.command(aliases=['money', 'coins'])
    async def wallet(self, ctx):
        stats = user_stats.get(ctx.author.id)
        money = stats.get('money')

        if ctx.author.name[-1] == 's':
            ap = '\''
        else:
            ap = '\'s'

        embed = discord.Embed(title=f'{ctx.author.name}{ap} wallet',
                              description=f'{self.coin}{money} coins',
                              color=0xFD6C6B)

        await ctx.send(embed=embed)


class Fishing(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.fishes = {
            'a boot':[0,90], 'seaweed':[0,90], 'water':[0,90],
            'a scuba diver':[0,90], 'a grenade':[0,90], 'a pair of crocs':[0,90],
            'a garden gnome':[1,50], 'a tadpole':[1,50], 'fish sticks':[1,50],
            'a cod':[1,50], 'a trout':[1,50], 'a salmon':[1,50], 'a burrito':[1,50],
            'a lobster':[1,50], 'corn nuts':[1,50], 'a catfish':[2,35], 
            'a frog':[2,35], 'a bass':[2,35], 'a pollock':[2,35], 'a couple dollars':[2,35],
            'a shark':[3,5], 'a solid gold fish':[3,5], 'a rolex':[3,5]
            }
        self.rarities = {0:'trash', 1:'common', 2:'rare', 3:'very rare'}
        self.coin = '<a:ccoin:958881860547665960>'
    
    @commands.group()
    @commands.cooldown(1, 5)
    async def fish(self, ctx):
        if ctx.invoked_subcommand == None:
            fished = random.choices(list(self.fishes), 
                                    weights=[d[1] for d in self.fishes.values()], 
                                    k=1)
            fish_name = fished[0]
            fish_info = self.fishes.get(fished[0])
            fish_type = self.rarities[fish_info[0]]

            stats = user_stats.get(ctx.author.id)
            current_money = stats.get('money')
            if current_money < 5:
                await ctx.send('You don\'t have enough money to fish!', delete_after=10)

            if stats.get('fish_stats') == None:
                user_stats.update(ctx.author.id, fish={'trash':0, 'common':0,
                                                    'rare':0, 'very rare':0})
                current_fish = stats.get('fish_stats')
            else:
                current_fish = stats.get('fish_stats')

            current_amount = current_fish.get(fish_type)

            current_fish.update({fish_type:current_amount+1})
            user_stats.update(ctx.author.id, fish=current_fish, money=current_money-5)

            embed = discord.Embed(description=f'You caught **{fish_name}**! ({fish_type})\n'
                                            f'You paid {self.coin}5 for casting',
                                  color=0xFD6C6B)
            await ctx.send(embed=embed)
    
    @fish.command(aliases=['inv'])
    async def inventory(self, ctx):
        stats = user_stats.get(ctx.author.id)
        fishes = stats.get('fish_stats')

        names = []
        for fish in fishes:
            names.append(f'**{fish.title()}** {"|"} {fishes.get(fish)}\n')

        names = ''.join(names)

        if ctx.author.name[-1] == 's':
            ap = '\''
        else:
            ap = '\'s'

        embed = discord.Embed(title=f'{ctx.author.name}{ap} inventory',
                              description=f'{names}',
                              color=0xFD6C6B)

        await ctx.send(embed=embed)

    @fish.command()
    async def sell(self, ctx, type):
        type = type.lower()
        stats = user_stats.get(ctx.author.id)
        fishes = stats.get('fish_stats')
        current_money = stats.get('money')

        sell_amount = fishes.get(type)
        if sell_amount == None or sell_amount == 0:
            return

        if type == 'trash':
            money_return = sell_amount * 3

        if type == 'common':
            money_return = sell_amount * 7

        if type == 'rare':
            money_return = sell_amount * 10

        if type == 'very rare':
            money_return = sell_amount * 20

        fishes.update({type:0})
        fish = fishes

        user_stats.update(ctx.author.id, fish=fish, money=current_money+money_return)

        embed = discord.Embed(description=f'You sold {sell_amount} {type} for {self.coin}{money_return}!',
                              color=0xFD6C6B)

        await ctx.send(embed=embed)


    @fish.error
    async def fish_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('Please slow down!!', delete_after=5)


def setup(bot):
    bot.add_cog(Farming(bot))
    bot.add_cog(Gambling(bot))
    bot.add_cog(Fishing(bot))