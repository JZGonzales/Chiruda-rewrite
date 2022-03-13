from MY_TOKEN import imgur_id, imgur_secret, approved_ids, imgur_access, imgur_refresh
from .Requests.request_handler import add_request
from petpetgif import petpet as petter
from imgurpython import ImgurClient
from typing import Union, Optional
from discord.ext import commands
from datetime import datetime
from io import BytesIO
import PIL

import requests
import discord
import random


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.imgur = ImgurClient(imgur_id, imgur_secret, refresh_token=imgur_refresh)
        self.imgur.set_user_auth(imgur_access, imgur_refresh)
        self.album_id = '91Cu8V6'


    @commands.command()
    async def ping(self, ctx):
        a = datetime.utcnow()
        b = ctx.message.created_at
        b = b.replace(tzinfo=None) - b.utcoffset()
        c = a - b
        await ctx.send(f'Pong! ({abs(round(c.total_seconds()*1000))}ms)')


    @commands.command(aliases=['cf'])
    async def coinflip(self, ctx):
        coin = random.randrange(0, 2)
        if coin == 0:
            await ctx.send('Heads!')
        else:
            await ctx.send('Tails!')


    @commands.group(invoke_without_command=True)
    async def art(self, ctx):
        images = self.imgur.get_album_images(self.album_id)
        urls = []
        for image in images:
            urls.append(image.link)
        embed=discord.Embed()
        embed.set_image(url=random.choice(urls))
        await ctx.send(embed=embed)


    @art.command()
    async def add(self, ctx):
        if ctx.author.id not in approved_ids:
            await ctx.send('You are not approved to add images!')
            return
        
        try:
            valid_types = ['image/png', 'image/jpeg', 'image/gif']
            filetype = ctx.message.attachments[0]
            if filetype.content_type not in valid_types:
                await ctx.send('Invalid file type!')
                return
            file = filetype.url
        except IndexError:
            file = ctx.message.content.split()
            file = file[2]
        
        image = self.imgur.upload_from_url(file, anon=False)
        print(image.get('id'))
        self.imgur.album_add_images(self.album_id, image.get('id'))
        embed=discord.Embed()
        embed.set_image(url=image.get('link'))
        await ctx.send(embed=embed)


    @commands.command()
    async def request(self, ctx, *, request):
        add_request({'Name':str(ctx.author), 'Request':request})
        await ctx.send('Request sent!')


    @commands.command()
    async def pet(self, ctx, image: Optional[Union[discord.PartialEmoji,
                                                   discord.member.Member,
                                                   discord.Attachment,
                                                   discord.Asset]]):
        if type(image) == discord.PartialEmoji:
            image = await image.read()
        elif type(image) == discord.member.Member:
            image = await image.avatar.with_format('png').read()
        else:
            url = ctx.message.content[5:]
            if len(url) == 0 and len(ctx.message.attachments) != 0:
                try:
                    valid_types = ['image/png', 'image/jpeg']
                    filetype = ctx.message.attachments[0]
                    if filetype.content_type not in valid_types:
                        await ctx.send('Invalid file type!')
                        return
                    image = await filetype.read()
                except IndexError:
                    await ctx.send('Invalid Emoji, Member or Image!')
                    return

            elif url.startswith('https://cdn.discordapp.com'):
                image = requests.get(url).content

            else:
                async for message in ctx.channel.history(limit=50):
                    valid_types = ['image/png', 'image/jpeg']
                    if len(message.attachments) > 0:
                        for img in message.attachments:
                            if img.content_type in valid_types:
                                image = await img.read()
                                break
                            break
        try:
            source = BytesIO(image)
            dest = BytesIO()
            petter.make(source, dest)
            dest.seek(0)
            await ctx.send(file=discord.File(dest, filename=f"{image[0]}-petpet.gif"))
        except PIL.UnidentifiedImageError:
            await ctx.send('Invalid argument!')


def setup(bot):
    bot.add_cog(General(bot))