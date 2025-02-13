import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
import asyncio
import random
from discord.commands import slash_command, Option
from discord.utils import get


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="Earn yourself a few coins")
    @commands.cooldown(1, 36000, commands.BucketType.user) #only once every 10h
    async def work(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND killed = 0")
        participant = cursor.fetchone()

        if not participant:
            await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)
        
            cursor.close()
            db.close()
            return
        
        if participant:
            amount = random.randint(2, 7)

            db = sqlite3.connect("players.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT coins FROM currency WHERE user = {ctx.author.id}")
            coins = cursor.fetchone()
            try:
                coins = coins[0]
            except:
                coins = 0

            cursor.execute("UPDATE currency SET coins = coins + ? WHERE user = ?", (amount, ctx.author.id))
            db.commit()
            cursor.close()
            db.close()
      
            embed = discord.Embed(description=f"You earned yourself **{amount} coins**! Your total balance is now **{coins + amount}** coins!", color=discord.Color.green())
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            await ctx.respond(embed=embed, ephemeral=True)

        
        log_channel = ctx.guild.get_channel(1163884909434253424)
        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/work` used')
        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
        embed.add_field(name="Earned coins:", value=amount, inline=False)            
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        await log_channel.send(embed=embed)  



def setup(bot):
    bot.add_cog(Work(bot))