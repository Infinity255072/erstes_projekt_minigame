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


class list(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description='Lists all participants')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def participants(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        desc = ""
        dead = ""

        for member in ctx.guild.members:
            cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 1", (member.id,))
            print(1)
            dead_check = cursor.fetchone()
            print(dead_check, "dead check check")
                
            if dead_check:
                print("dead check", member)
                user = ctx.guild.get_member(member.id)
                dead += f"- {user}\n"


            cursor.execute(f"SELECT user FROM players WHERE user = {member.id} AND killed = 0")
            participant = cursor.fetchone()

            if not participant:
                continue

            user = ctx.guild.get_member(member.id)
            desc += f"- {user}\n"
            
        if desc == "":
            desc = "There are currently no players in the game!"
        print(dead)
        embed = discord.Embed(color=discord.Color.orange(), description="Alive:\n\n"+ desc)
        embed.add_field(name="Dead:", value=dead)
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        embed.timestamp = discord.utils.utcnow()
        await ctx.respond(embed=embed, ephemeral=True)

        db.commit()
        cursor.close()
        db.close()


def setup(bot):
    bot.add_cog(list(bot))