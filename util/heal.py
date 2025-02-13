import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
from discord.commands import slash_command, Option
from discord.utils import get
import random


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Heal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="Heal youself")
    async def heal(self, ctx, item: Option(str, "Select the item you want to heal yourself with", choices=["Bandage", "Medkit"])):
        selected_item = str(item)
        
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND killed = 0")
        participant = cursor.fetchone()

        if not participant:
            await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)

            cursor.close()
            db.close()
            return
        
        
        cursor.execute("SELECT item FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, selected_item))
        item = cursor.fetchone()

        if item:
            item = str(item[0])
            if selected_item == "Bandage":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Bandage'))
                bandage = cursor.fetchone()

                if not bandage:
                    cursor.close()
                    db.close()
                    return await ctx.respond(":x:︱You don't have a bandage to heal yourself!", ephemeral=True)

                if bandage:
                    cursor.execute("UPDATE items SET amount = amount -1 WHERE user =? AND item = ?", (ctx.author.id, selected_item))

                    cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("hunter",))
                    hunter = cursor.fetchone()
    
                    if hunter:
                        cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
                        health = cursor.fetchone()

                        try:
                            health = health[0]
                        except:
                            health = 0

                        health = health +1

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

                        await ctx.respond(f':adhesive_bandage:︱You succesfully healed yourself with a bandage! You gained 1 HP.', embed=embed, ephemeral=True)

                        cursor.execute("UPDATE players SET health = health +1 WHERE user =? AND role = ?", (ctx.author.id, "hunter"))

                        db.commit()
                        cursor.close()
                        db.close()

                    
                    if not hunter:
                        cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
                        health = cursor.fetchone()

                        try:
                            health = health[0]
                        except:
                            health = 0

                        health = health +1

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
                        description=f"Health: {health}/15\n{health_bar}",
                        color=em_color)

                        db.commit()
                        cursor.close()
                        db.close()

                        await ctx.respond(f':adhesive_bandage:︱You succesfully healed yourself with a bandage! You gained 1 HP.', embed=embed, ephemeral=True)

                        cursor.execute("UPDATE players SET health = health +1 WHERE user =? AND role = ?", (ctx.author.id, "creature"))
                        
                        db.commit()
                        cursor.close()
                        db.close()

                        log_channel = ctx.guild.get_channel(1163884909434253424)
                        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/heal` used')
                        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        await log_channel.send(embed=embed)  



            if selected_item == "Medkit":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Medkit'))
                medkit = cursor.fetchone()

                if not medkit:
                    cursor.close()
                    db.close()
                    return await ctx.respond(":x:︱You don't have a medkit to heal yourself!", ephemeral=True)

                if medkit:
                    cursor.execute("UPDATE items SET amount = amount -1 WHERE user =? AND item = ?", (ctx.author.id, selected_item))

                    cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("hunter",))
                    hunter = cursor.fetchone()
    
                    if hunter:
                        cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
                        health = cursor.fetchone()

                        try:
                            health = health[0]
                        except:
                            health = 0

                        health = health +3

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


                        await ctx.respond(f':adhesive_bandage:︱You succesfully healed yourself with a medkit! You gained 3 HP.', embed=embed, ephemeral=True)

                        cursor.execute("UPDATE players SET health = health +3 WHERE user =? AND role = ?", (ctx.author.id, "hunter"))

                        db.commit()
                        cursor.close()
                        db.close()

                        log_channel = ctx.guild.get_channel(1163884909434253424)
                        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/heal` used')
                        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        await log_channel.send(embed=embed)  

                    
                    if not hunter:
                        cursor.execute(f"SELECT health FROM players WHERE user = {ctx.author.id}")
                        health = cursor.fetchone()

                        try:
                            health = health[0]
                        except:
                            health = 0

                        health = health +3

                        health = min(health, 15)

                        lost_health = 15 - health

                        health_bar = "▰" * health + "▱" * lost_health


                        em_color = discord.Color.green()
                        if health == 10 or health == 9 or health == 8 or health == 7 or health == 6:
                            em_color = discord.Color.orange()
            
                        if health <= 5:
                            em_color = discord.Color.red()
            

                        embed = discord.Embed(
                        title=f"{ctx.author.display_name}'s health",
                        description=f"Health: {health}/15\n{health_bar}",
                        color=em_color)


                        await ctx.respond(f':adhesive_bandage:︱You succesfully healed yourself with a medkit! You gained 3 HP.', embed=embed, ephemeral=True)

                        cursor.execute("UPDATE players SET health = health +3 WHERE user =? AND role = ?", (ctx.author.id, "creature"))
                        
                        db.commit()
                        cursor.close()
                        db.close()


                        log_channel = ctx.guild.get_channel(1163884909434253424)
                        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/heal` used')
                        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        await log_channel.send(embed=embed)  
                    
        if not item:
            cursor.close()
            db.close()
            return await ctx.respond(f":x:︱You don't have a {str(selected_item.lower())} to heal yourself!", ephemeral=True)


def setup(bot):
    bot.add_cog(Heal(bot))