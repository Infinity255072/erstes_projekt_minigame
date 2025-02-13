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


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description='Displays information about a user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def info(self, ctx, member: Option(discord.Member, "The user you want to see the information from")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {member.id} AND killed = 0")
        participant = cursor.fetchone()

        if participant:
            cursor.execute(f"SELECT user, role, health, trapped FROM players WHERE user = {member.id}")
            info = cursor.fetchone()
            cursor.execute(f"SELECT coins FROM currency WHERE user = {member.id}")
            coins = cursor.fetchone()

            role = str(info[1])
            health = str(info[2])
            trapped = str(info[3])

            if trapped == "0":
                trapped = "False"
            if trapped == "1":
                trapped = "True"

            try:
                coins = str(coins[0])
            except:
                coins = 0


            cursor.execute(f"SELECT * FROM items WHERE user = {member.id} AND amount > 0")
            result = cursor.fetchall()

            desc = ""

            for index, item in enumerate(result):
                desc += f"**{item[2]} - {item[1]}**\n"
            

            embed = discord.Embed(color=discord.Color.orange(), description=f"**Items:**\n{desc}")
            embed.set_author(name=f"{member.name}", icon_url=member.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            embed.add_field(name=f"Role:", value=f"{role}")
            embed.add_field(name=f"Health:", value=f"{health}")
            embed.add_field(name=f"Trapped:", value=f"{trapped}")
            embed.add_field(name=f"Coins:", value=f"{coins}")
            await ctx.respond(embed=embed, ephemeral=True)

        if not participant:
            cursor.close()
            db.close()
            await ctx.respond(f"{member.mention} is either dead or not participating in the game!", ephemeral=True)



def setup(bot):
    bot.add_cog(Info(bot))