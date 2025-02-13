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


class Trap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="[Creature] traps a hunter")
    @commands.cooldown(1, 86400, commands.BucketType.user) #only once per day
    async def trap(self, ctx, hunter: Option(discord.Member, "The hunter you want to trap")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ?", ("killercooldown",))
        cooldown = cursor.fetchone()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("creature",))
        creature = cursor.fetchone()
    
        if creature and not cooldown:
            if hunter.id == ctx.author.id:
                self.trap.reset_cooldown(ctx)
                cursor.close()
                db.close()
                return await ctx.respond(f":x:︱You can't trap yourself, {ctx.author.mention}!", ephemeral=True)
            cursor.execute(f"SELECT user FROM players WHERE user = {hunter.id} AND role = ? AND killed = 0", ("hunter",))
            hunter_check = cursor.fetchone()

            if hunter_check:
                cursor.execute("UPDATE players SET trapped = ? WHERE user =?", (1, hunter.id))

                db.commit()
                cursor.close()
                db.close()

                channel = ctx.guild.get_channel(1163909997126746223) #change
                await channel.set_permissions(hunter, read_messages=True, send_messages=False)

                embed = discord.Embed(color=discord.Color.red(), description=f':chains:︱You succesfully trapped {hunter.mention}!')
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                embed.timestamp = discord.utils.utcnow()
                
                await ctx.respond(embed=embed, ephemeral=True)

                embed = discord.Embed(color=discord.Color.orange(), description=f":chains:︱You got trapped by the creature! The trap lasts 1 hour.")
                embed.set_author(name=f"{hunter.name}", icon_url=hunter.display_avatar)
                embed.timestamp = discord.utils.utcnow()
                embed.set_image(url="https://alexonfilm.files.wordpress.com/2019/03/halloween183.jpg")
                await hunter.send(f"{hunter.mention}", embed=embed)

                log_channel = ctx.guild.get_channel(1163884909434253424)
                embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/trap` used')
                embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
                embed.add_field(name="Used on:", value=f'{hunter.display_name}', inline=False)
                embed.timestamp = discord.utils.utcnow()
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                await log_channel.send(embed=embed)

                await asyncio.sleep(21600) 

                db = sqlite3.connect("players.sqlite")
                cursor = db.cursor()

                cursor.execute(f"SELECT user FROM players WHERE user = {hunter.id} AND role = ? AND killed = 0", ("hunter",))
                alive = cursor.fetchone()

                if alive:
                    cursor.execute("UPDATE players SET trapped = ? WHERE user =?", (0, hunter.id))

                    embed = discord.Embed(color=discord.Color.orange(), description=f":chains::boom:︱You freed yourself from the trap!")
                    embed.set_author(name=f"{hunter.name}", icon_url=hunter.display_avatar)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_image(url="https://de.web.img3.acsta.net/r_654_368/newsv7/18/09/27/08/47/0998879.jpg")
                    await hunter.send(f"{hunter.mention}", embed=embed)

                    channel = ctx.guild.get_channel(1163909997126746223)
                    await channel.set_permissions(hunter, read_messages=True, send_messages=True)

                    db.commit()
                    cursor.close()
                    db.close()

                

            
            if not hunter_check:
                self.trap.reset_cooldown(ctx)
                cursor.close()
                db.close()

                return await ctx.respond(f"{hunter.mention} is not a hunter!", ephemeral=True)
            


        if not creature:
            self.trap.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You are not the creature!', ephemeral=True)
        
        if cooldown:
            self.trap.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You cant use this command today!', ephemeral=True)
        

    



def setup(bot):
    bot.add_cog(Trap(bot))