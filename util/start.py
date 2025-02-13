import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
import asyncio
import os
from discord.commands import slash_command, Option
from discord.utils import get
import random


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @bot.command()
    async def day2(self, ctx):
        if ctx.author.id != 383115054431731726 and ctx.author.id != 192291195475591168 and ctx.author.id != 1152714944840749156:
            return
        
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute("INSERT INTO players(user, clues) VALUES (?, ?)", ("day", "2"))
        db.commit()
        cursor.execute("INSERT INTO players(user, clues) VALUES (?, ?)", ("killercooldown", "2"))

        db.commit()

        participants = []

        for member in ctx.guild.members:
            cursor.execute(f"SELECT user FROM players WHERE user = ?", (member.id,))
            participant = cursor.fetchone()
        
            if participant:
                print(member)
                participants.append(member.id)
                cursor.execute("UPDATE players SET role = ? WHERE user =?", ('hunter', member.id))
                print(23)
                cursor.execute("UPDATE players SET health = ? WHERE user =? AND role = ?", (5, member.id, "hunter"))
                print(34)


        num_creatures = 1
        
        voice_channel = ctx.guild.get_channel(1163910834456625273)

        creatures_mentions = []

        for i in range(num_creatures):
            print(num_creatures)
            creature = random.choice(participants)
            print(creature)
        
            creature_user = ctx.guild.get_member(creature)
            print(creature_user)
            cursor.execute("UPDATE players SET role = ? WHERE user =?", ('creature', creature))
            db.commit()
            print(456)
            cursor.execute("UPDATE players SET health = ? WHERE user =? AND role = ?", (20, creature, "creature"))
            db.commit()
            print(345567)
            channel = ctx.guild.get_channel(1163909997126746223)
            creature_chat = ctx.guild.get_channel(1163910092027072512)
            await channel.set_permissions(creature_user, read_messages=True, send_messages=True)
            await creature_chat.set_permissions(creature_user, read_messages=True, send_messages=True)

            await voice_channel.set_permissions(creature_user, speak=True)
            creatures_mentions.append(creature_user.mention)

            participants.remove(creature)


        hunters_mentions = [ctx.guild.get_member(user_id).mention for user_id in participants]


        for user in participants:
            user = ctx.guild.get_member(user)
            await voice_channel.set_permissions(user, speak=True)

            embed = discord.Embed(color=discord.Color.orange(), description=f'{user.mention} you are a **hunter**!')
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()

            cursor.execute("INSERT INTO items VALUES (?, ?, 1)", (user.id, "Knife"))
            db.commit()
            try:
                await user.send(embed=embed)
            except:
                continue

            channel = ctx.guild.get_channel(1163909997126746223)
            await channel.set_permissions(user, read_messages=True, send_messages=True)



            db.commit()
        cursor.close()
        db.close()
            
        for i in range(num_creatures):
            user = ctx.guild.get_member(creature)

            embed = discord.Embed(color=discord.Color.orange(), description=f'{user.mention} you are the **creature**!')
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()

            await user.send(embed=embed)
            


        embed = discord.Embed(
            color=discord.Color.orange(),
            description=":white_check_mark:︱Day 2 has started and the roles are given.",
        )
        embed.add_field(name="Hunters:", value=" ".join(hunters_mentions), inline=False)
        embed.add_field(name="Creatures:", value=" ".join(creatures_mentions), inline=False)
        embed.add_field(name="ㅤ", value="A message has been sent to all participants.", inline=False)
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        embed.timestamp = discord.utils.utcnow()
        channel = ctx.guild.get_channel(1163883791601901719)
        await channel.send(embed=embed)

        participants.clear()
        creatures_mentions.clear()


def setup(bot):
    bot.add_cog(Start(bot))