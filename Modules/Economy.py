import datetime
import random
import json
import discord

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

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def determine_money(self, num):
        if num in range(10, 91):
            s_num = str(num)
            num = int(s_num[0])*3
            return num

        if num < 10:
            return 0

        if num > 90:
            return 100


    @commands.command()
    async def plant(self, ctx):
        stats = us.get_stats(ctx.author)
        coins = stats.get('coins')
        if coins - 15 < 0:
            await ctx.send('You don\'t have enough coins to plant!', delete_after=5)
            return
        if stats.get('farm_planted'):
            await ctx.send('You must harvest your farm first!', delete_after=5)
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        time = now + datetime.timedelta(minutes=10)
        next_harvest = time.isoformat()

        us.update_stats(ctx.author, farm_planted=True, yield_amount=random.randrange(0, 100),
                        next_harvest=next_harvest, coins=coins-15)

        embed = discord.Embed(title='Crops planted!',
                              description=f'You paid {COIN}15 for crops',
                              color=COLOR)
        embed.set_footer(text='You can harvest in 10 minutes', icon_url=discord.Embed.Empty)

        await ctx.send(embed=embed)

    @commands.command()
    async def harvest(self, ctx):
        stats = us.get_stats(ctx.author)
        harvest_time = stats.get('next_harvest')

        if not stats.get('farm_planted'):
            await ctx.send('You must plant your farm first!')
            return

        if datetime.datetime.fromisoformat(harvest_time) > datetime.datetime.now(datetime.timezone.utc):
            time_left = datetime.datetime.fromisoformat(harvest_time) - datetime.datetime.now(datetime.timezone.utc)
            _, minutes, seconds = str(time_left).split(':')
            # Purely cosmetic if statement
            if minutes == '0':
                await ctx.send(f'You can harvest in {seconds[:2]} seconds!', delete_after=10)
            
            else:
                await ctx.send(f'You can harvest in {minutes} minutes and {seconds[:2]} seconds!', delete_after=10)
            return

        profit = self.determine_money(stats.get('yield_amount'))
        coins = stats.get('coins')
        current_harvests = stats.get('total_harvests')

        us.update_stats(ctx.author, farm_planted=False, coins=coins+profit,
                        total_harvests=current_harvests+1, next_harvest=False)

        embed = discord.Embed(title='Crops harvested!',
                              description=f'You gained {COIN}{profit} from this harvest!',
                              color=COLOR)
        embed.set_footer(text='Use ~plant to plant more crops', icon_url=discord.Embed.Empty)

        await ctx.send(embed=embed)


    async def get_item_inventory(self):
        pass


    @commands.command()
    async def shop(self, ctx):
        V = View(timeout=None)

        # All purchasable items
        items = {'⏩ Boosts':{
                    'boost2':['2 minute boost', 50], 
                    'boost5':['5 minute boost', 100]
                    },
                 '🌱 Fertilizers':{
                    'harvest2x':['Double harvest', 50]
                    }
                }

        #This is just for proper embed length
        SEPERATOR = '\u2800'*15
        
        select = Select(placeholder='Please select an upgrade here!')
        embed = discord.Embed(title='Item shop',
            description=f'Purchase items to boost your farms productivity!{SEPERATOR}',
            color=COLOR)


        async def get_inventory():
            # Yes I know this is inefficient.
            stats = us.get_stats(ctx.author)
            inventory = []
            for category, item_data in  zip(list(items), list(items.values())):
                for name, data in zip(list(item_data), list(item_data.values())):
                    inventory.append(f'{category[0]} {data[0]} | {stats.get(name)}')
            inventory.append(f"{COIN}{stats.get('coins')}")
            return inventory

        
        for category, item_data in  zip(list(items), list(items.values())):
            select.add_option(label=category[2:], 
                              emoji=category[0],
                              value=category)
            field_values = []
            for name, data in zip(list(item_data), list(item_data.values())):
                field_values.append(f'{data[0]} | {COIN}{data[1]}')

            embed.add_field(name=category, value='\n'.join(field_values))
        embed.insert_field_at(0, name=f'{ctx.author.name}{__ap__(ctx.author.name)} inventory', 
                              value='\n'.join(await get_inventory()),
                              inline=False)


        async def view_check(cb):
            return cb.user == ctx.author


        async def buy_callback(cb):
            # custom id for buttons is a stringified list
            # so we can grab the correct data quicker
            stats = us.get_stats(ctx.author)
            category, item = json.loads(cb.data.get('custom_id'))
            item_type = items.get(category)
            price = item_type.get(item)[1]

            name = embed.fields[0].name
            kwargs = {
                'coins':stats.get('coins')-price,
                item:stats.get(item)+1
                }

            us.update_stats(
                ctx.author, 
                **kwargs)

            embed.set_field_at(
                0,
                name=name,
                value='\n'.join(await get_inventory()),
                inline=False)
            
            await cb.response.edit_message(embed=embed)

        
        async def select_callback(cb):
            buy_type = cb.data.get('values')[0]
            V.clear_items()

            for item_nickname, item_info in zip(
                items.get(buy_type), 
                items.get(buy_type).values()
                ):
                item_name, value = item_info
                button = Button(
                    custom_id=f'["{buy_type}", "{item_nickname}"]',
                    emoji=COIN,
                    label=f'{value}\u2800{item_name}')

                button.callback = buy_callback
                button.style = discord.ButtonStyle.primary
                V.add_item(button)

            await ctx.message.delete()
            await cb.message.delete()
            await cb.response.send_message(embed=embed, view=V, ephemeral=True)

        
        select.callback = select_callback
        V.add_item(select)
        V.interaction_check = view_check
        
        await ctx.send(embed=embed, view=V)

    
    @commands.command()
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


    @commands.command(aliases=['money', 'coins'])
    async def wallet(self, ctx):
        stats = us.get_stats(ctx.author)
        coins = stats.get('coins')

        embed = discord.Embed(title=f'{ctx.author.name}{__ap__(ctx.author.name)} wallet',
                              description=f'{COIN}{coins:,} coins',
                              color=COLOR)

        await ctx.send(embed=embed)


    @commands.group()
    @commands.cooldown(1, 5)
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

    
    @fish.command(aliases=['inv'])
    async def inventory(self, ctx):
        stats = us.get_stats(ctx.author)
        inventory = {
            'trash':stats.get('fish_trash'),
            'common':stats.get('fish_common'),
            'uncommon':stats.get('fish_uncommon'),
            'rare':stats.get('fish_rare')
        }
        # list being joined is formatted as 'name amount'
        name = '\n'.join([f'{e}{SEP*3}' for e in list(inventory)])
        amount = '\n'.join([str(f) for f in list(inventory.values())])
        embed = discord.Embed(
            title=f'{ctx.author.name}{__ap__(ctx.author.name)} inventory',
            color=COLOR
        )
        embed.add_field(name='Fishes', value=name)
        embed.add_field(name=SEP, value=amount)
        embed.set_footer(text=f'{stats.get("coins"):,} coins', icon_url=embed.Empty)
        await ctx.send(embed=embed)

    
    @fish.command()
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
    bot.add_cog(Economy(bot))
