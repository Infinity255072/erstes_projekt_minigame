import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
import asyncio
import json
import os
from discord.commands import slash_command, Option
from discord.utils import get


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS currency(user INTEGER, coins)")
        cursor.execute("CREATE TABLE IF NOT EXISTS items(user INTEGER, item TEXT, amount INTEGER)")

        db.commit()
        cursor.close()
        db.close()

    
    @bot.slash_command(description="Displays your current coin balance")
    async def coins(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id}")
        participant = cursor.fetchone()

        if not participant:
            cursor.close()
            db.close()
            return await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)

        cursor.execute(f"SELECT coins FROM currency WHERE user = {ctx.author.id}")
        coins = cursor.fetchone()

        try:
            coins = coins[0]
        except:
            coins = 0

        db.commit()
        cursor.close()
        db.close()

        embed = discord.Embed(
            color=discord.Color.orange()
        )
        embed.set_author(name=f"{ctx.author.name}'s coins", icon_url=ctx.author.display_avatar)
        embed.add_field(name="Coins:", value=f":coin: {coins}", inline=False)
        embed.timestamp = discord.utils.utcnow()

        await ctx.respond(embed=embed, ephemeral=True)

        log_channel = ctx.guild.get_channel(1163884909434253424)
        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/coins` used')
        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        await log_channel.send(embed=embed)  


def setup(bot):
    bot.add_cog(Currency(bot))