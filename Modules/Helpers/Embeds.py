import discord
Empty = discord.Embed.Empty
def make_embed(
    title=Empty,
    description=Empty,
    url=Empty,
    color=Empty,
    footer=[Empty, Empty],
    image=Empty,
    thumbnail=Empty,
    author=Empty,
    fields=Empty,
    ):
    
    
    embed=discord.Embed(
        title=title,
        description=description,
        url=url,
        color=color
    )

    embed.set_footer(text=footer[0], icon_url=footer[1])
    if image != Empty:
        embed.set_image(url=image)
    if thumbnail != Empty:
        embed.set_thumbnail(url=thumbnail)

    if author != Empty:
        try:
            embed.set_author(name=author[0], url=author[1], icon_url=author[2])
        except:
            embed.set_author(name='\u200b', url=author[1], icon_url=author[2])

    if fields != Empty:
        for field in fields:
            try:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
            except:
                embed.add_field(name='\u200b', value=field[1], inline=field[2])

    return embed