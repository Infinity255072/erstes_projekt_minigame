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


class Health(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="Displays your current health")
    async def health(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("hunter",))
        hunter = cursor.fetchone()
    
        if hunter:
            cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
            health = cursor.fetchone()

            try:
                health = health[0]
            except:
                health = 0

            health = min(health, 5)
            lost_health = 5 - health
            health_bar = "▰" * health + "▱" * lost_health


            em_color = discord.Color.green()

            if health == 3:
                em_color = discord.Color.orange()
            
            if health <= 2:
                em_color = discord.Color.red()

            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s health",
                description=f"Health: {health}/5\n{health_bar}",
                color=em_color
            )

            db.commit()
            cursor.close()
            db.close()

            await ctx.respond(embed=embed, ephemeral=True)



        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("creature",))
        creature = cursor.fetchone()
    
        if creature:
            cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
            health = cursor.fetchone()

            try:
                health = health[0]
            except:
                health = 0

            health = min(health, 20)

            lost_health = 20 - health

            health_bar = "▰" * health + "▱" * lost_health


            em_color = discord.Color.green()
            if health == 10 or health == 9 or health == 8 or health == 7 or health == 6:
                em_color = discord.Color.orange()
            
            if health <= 5:
                em_color = discord.Color.red()
            

            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s health",
                description=f"Health: {health}/20\n{health_bar}",
                color=em_color
            )
            db.commit()
            cursor.close()
            db.close()
            
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            cursor.close()
            db.close()
            await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)
            
        log_channel = ctx.guild.get_channel(1163858592374476941)
        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/health` used')
        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        await log_channel.send(embed=embed)  
            

            

def setup(bot):
    bot.add_cog(Health(bot))