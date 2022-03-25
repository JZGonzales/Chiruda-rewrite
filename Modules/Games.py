from .Helpers.word_list import words, allowed_words, emotes
from discord.ext import commands

import discord
import random
import string

class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.word = None
        self.guesses = 1
        self.color_matrix = []
        self.bad_letters = []

        self.embed = None
        self.message = None


    async def color_array(self, guess) -> list:
        green = '🟩'
        yellow = '🟨'
        black = '⬛'

        colors = []
        green_letters = []

        for guess_letter, word_letter in zip(guess, self.word):
            if guess_letter == word_letter:
                colors.append(green)
                green_letters.append(guess_letter)
            
            elif (guess_letter in self.word and
                  guess_letter not in green_letters):
                colors.append(yellow)

            else:
                colors.append(black)
                if guess_letter not in green_letters:
                    self.bad_letters.append(guess_letter)
            
        colors.append(f' {guess}')

        return colors


    async def str_to_emote(self, guess):
        if self.bad_letters == []:
            return '\u200b'


        alph = list(string.ascii_lowercase)
        new_letters = []

        for letter in self.bad_letters:
            get_index = alph.index(letter)
            if emotes[get_index] not in new_letters:
                new_letters.append(emotes[get_index])

        new_letters.sort()
        return ' '.join(new_letters)


    @commands.group(aliases=['w'],
                    description='Starts a new wordle game')
    async def wordle(self, ctx):

        if ctx.invoked_subcommand == None:
            # Reset init values for new game
            self.word = random.choice(words)
            self.bad_letters = []
            self.color_matrix = []
            self.guesses = 1

            # New game embed setup
            embed = discord.Embed(title='Wordle!',
                                  description='Guess the word with ~w guess [word]!')
            
            embed.add_field(name='Guesses',
                            value='\u200b',
                            inline=False)
            embed.add_field(name='Incorrect letters',
                            value='\u200b',
                            inline=False)

            self.embed = embed
            self.message = await ctx.send(embed=embed)


    @wordle.command(description='Used to guess the word in a wordle game')
    async def guess(self, ctx, guess:str):
        # Make sure guess is lowercase to do string matching
        embed = self.embed
        guess = guess.lower()

        # Checks
        if guess not in allowed_words:
            await ctx.send('That\'s not a valid word!')
            return

        if self.guesses == None:
            return

        if self.guesses < 7:
            self.color_matrix.append(await self.color_array(guess))

            str_matrix = '\n'.join(''.join(str(i) for i in x) for x in self.color_matrix)

            embed.clear_fields()
            embed.add_field(name='Guesses',
                            value=str_matrix,
                            inline=False)
            embed.add_field(name='Incorrect letters',
                            value=await self.str_to_emote(guess),
                            inline=False)
            
            if guess == self.word:
                embed.set_footer(text=f'The word was {self.word}! Excellent!',
                                 icon_url=discord.Embed.Empty)
                self.guesses = None
            
            try:
                self.guesses += 1
            except:
                pass

        else:
            embed.set_footer(text=f'The word was {self.word}. Game over :(',
                             icon_url=discord.Embed.Empty)

        await self.message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Games(bot))