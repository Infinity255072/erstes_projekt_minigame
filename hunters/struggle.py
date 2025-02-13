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


class Struggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="[Hunter] try to free yourself from being trapped")
    @commands.cooldown(1, 86400, commands.BucketType.user) #only once per day
    async def struggle(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ? AND killed = 0", ("hunter",))
        hunter = cursor.fetchone()
    
        if hunter:
            cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ? AND trapped = 1", ("hunter",))
            trapped = cursor.fetchone()

            if trapped:
                chance = random.randint(1, 100)

                if chance <= 30:
                    success = "True"
                    embed = discord.Embed(color=discord.Color.green(), description=f":chains::boom:︱You've managed to free yourself from the trap!")
                    embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_image(url="https://media.gq-magazin.de/photos/617283913f79fd7c589247ec/16:9/w_2560%2Cc_limit/Halloween%2520Kills.jpg")
                    await ctx.respond(f"{ctx.author.mention}", embed=embed, ephemeral=True)

                    cursor.execute("UPDATE players SET trapped = ? WHERE user =?", (0, ctx.author.id))

                    db.commit()
                    cursor.close()
                    db.close()

                    channel = ctx.guild.get_channel(1163909997126746223)
                    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)


                else:
                    success = "False"
                    db.commit()
                    cursor.close()
                    db.close()

                    embed = discord.Embed(color=discord.Color.red(), description=f":chains:︱You you didn't manage to free yourself from the trap...")
                    embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_image(url="https://alexonfilm.files.wordpress.com/2019/03/halloween183.jpg")
                    await ctx.respond(f"{ctx.author.mention}", embed=embed, ephemeral=True)

                    log_channel = ctx.guild.get_channel(1163884909434253424)
                    embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/struggle` used')
                    embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
                    embed.add_field(name="Success:", value=f'{success}', inline=False)
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                    await log_channel.send(embed=embed)  
            

            
            if not trapped:
                self.struggle.reset_cooldown(ctx)
                cursor.close()
                db.close()

                return await ctx.respond(f":x:︱You are currently not trapped!", ephemeral=True)
            

        if not hunter:
            self.struggle.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond(f":x:︱You aren't a hunter!", ephemeral=True)
        
            




def setup(bot):
    bot.add_cog(Struggle(bot))