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


items = {
    "Handgun": 7,
    "Handgun ammo": 2,
    "Rifle": 10,
    "Rifle ammo": 3,
    "Shotgun": 13,
    "Shotgun ammo": 3,
    "Bandage": 2,
    "Medkit": 5

}

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description='Deletes all data out of the database from a specific user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def delete_data(self, ctx, member: Option(discord.Member, "The user you want to delete the data from")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {member.id} AND killed = 0")
        participant = cursor.fetchone()

        if participant:
            cursor.execute(f"DELETE FROM players WHERE user = ?", (member.id,))
            cursor.execute(f"DELETE FROM currency WHERE user = ?", (member.id,))
            cursor.execute(f"DELETE FROM items WHERE user = ?", (member.id,))

            embed = discord.Embed(color=discord.Color.orange(), description=f':white_check_mark:︱Succesfully deleted all data from {member.mention}')
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            await ctx.respond(embed=embed, ephemeral=True)

            db.commit()
            cursor.close()
            db.close()

        if not participant:
            cursor.close()
            db.close()
            await ctx.respond(f"{member.mention} is either dead or not participating in the game!", ephemeral=True)


    @bot.slash_command(description='Adds a user to the game [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def add_data(self, ctx, member: Option(discord.Member, "The user you want to add the data"), role_add: Option(str, "Choose the role the person should have when added", choices=["hunter", "creature"])):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ? AND role = ? OR role = ?", (member.id,), "hunter", "creature")
        participant = cursor.fetchone()

        if not participant:
            cursor.execute("INSERT INTO players(user, health, trapped, killed) VALUES (?, ?, ?, ?)", (member.id, 0, 0, 0,))
            db.commit()
            cursor.execute("UPDATE players SET role = ? WHERE user =?", (str(role_add), member.id))
            db.commit()
            if str(role_add) == "hunter":
                cursor.execute("UPDATE players SET health = ? WHERE user =? AND role = ?", (5, member.id, "hunter"))
                db.commit()
            if str(role_add) == "creature":
                cursor.execute("UPDATE players SET health = ? WHERE user =? AND role = ?", (15, member.id, "creature"))
                db.commit()
            cursor.execute("INSERT INTO items VALUES (?, ?, 1)", (member.id, "Knife"))
            cursor.execute("INSERT INTO currency(user, coins) VALUES (?, ?)", (member.id, 0))

            embed = discord.Embed(color=discord.Color.orange(), description=f':white_check_mark:︱Succesfully added {member.mention} to the database!')
            embed.set_author(name=f"{member.name}", icon_url=member.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            await ctx.respond(embed=embed, ephemeral=True)

            db.commit()
            cursor.close()
            db.close()

        if participant:
            cursor.close()
            db.close()
            await ctx.respond(f"{member.mention} is either dead or participating in the game!", ephemeral=True)


    @bot.slash_command(description='Revives a user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def admin_revive(self, ctx, member: Option(discord.Member, "The user you want to revive")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {member.id} AND killed = 1")
        killed = cursor.fetchone()

        if killed:
            cursor.execute("UPDATE players SET killed = 0 WHERE user =?", (member.id,))
            cursor.execute("UPDATE players SET health = 5 WHERE user =?", (member.id,))

            db.commit()
            cursor.close()
            db.close()

            channel = ctx.guild.get_channel(1163909997126746223)
            await channel.set_permissions(member, read_messages=True, send_messages=True)
            voice_channel = ctx.guild.get_channel(1158538430876225557)
            await voice_channel.set_permissions(member, speak=True)

            embed = discord.Embed(color=discord.Color.orange(), description=f':white_check_mark:︱Succesfully revived {member.mention}!')
            embed.set_author(name=f"{member.name}", icon_url=member.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            await ctx.respond(embed=embed, ephemeral=True)

        if not killed:
            await ctx.respond(f"{member.mention} is either not dead or not participating in the game!", ephemeral=True)







    @bot.slash_command(description='Kills a user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def admin_kill(self, ctx: discord.ApplicationContext, hunter: Option(discord.Member, "The hunter you want to kill")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        if hunter.id == ctx.author.id:
            cursor.close()
            db.close()
            return await ctx.respond(f":x:︱You can't kill yourself, {ctx.author.mention}!", ephemeral=True)
            
        cursor.execute(f"SELECT user FROM players WHERE user = {hunter.id} AND role = ? AND killed = 0", ("hunter",))
        hunter_check = cursor.fetchone()

        if hunter_check:
            cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, hunter.id))
            cursor.execute("UPDATE players SET health = 0 WHERE user =?", (hunter.id,))

            db.commit()
            cursor.close()
            db.close()

            channel = ctx.guild.get_channel(1163909997126746223) 
            await channel.set_permissions(hunter, read_messages=True, send_messages=False)


            embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {hunter.mention}!')
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()
                
            await ctx.respond(embed=embed, ephemeral=True)

            embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
            embed.set_author(name=f"{hunter.name}", icon_url=hunter.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
            await hunter.send(embed=embed)

            log_channel = ctx.guild.get_channel(1163884909434253424)
            embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/admin_kill` used')
            embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
            embed.add_field(name="Used on:", value=f'{hunter.display_name}', inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            await log_channel.send(embed=embed)

            voice_channel = ctx.guild.get_channel(1163910834456625273)
            await voice_channel.set_permissions(hunter, speak=False)

            channel = ctx.guild.get_channel(1163909997126746223)
            embed = discord.Embed(color=discord.Color.red(), description=f"{hunter.mention} was found dead! Their cause of death is currently unknown.")
            embed.set_author(name=f"{hunter.name}", icon_url=hunter.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            await asyncio.sleep(1800)
            await channel.send("<@&961745027158122557>", embed=embed)
                

            
            if not hunter_check:
                self.kill.reset_cooldown(ctx)
                cursor.close()
                db.close()

                return await ctx.respond(f"{hunter.mention} is not a hunter!", ephemeral=True)
            



    @bot.slash_command(description='Adds an item to a users inventory')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def give_item(self, ctx: discord.ApplicationContext, user: Option(discord.Member, "The user you want to give the item to"), item: Option(str, "Select the item you want to give", choices=list(items.keys()))):
        selected_item = str(item)

        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()


        if selected_item in items:
            cursor.execute("SELECT * FROM items WHERE user =? AND item =?", (user.id, item))
            item_check = cursor.fetchone()

            embed = discord.Embed(description=f"You succesfully gave **1 {selected_item}** to {user.display_name}!",
                                  color=discord.Color.orange())
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()

            if item_check:
                cursor.execute("UPDATE items SET amount = amount +1 WHERE user =? AND item = ?", (user.id, selected_item))
                db.commit()
                cursor.close()
                db.close()
                await ctx.respond(embed=embed, ephemeral=True)

            else:
                cursor.execute("INSERT INTO items VALUES (?, ?, 1)", (user.id, selected_item))
                db.commit()
                cursor.close()
                db.close()
                await ctx.respond(embed=embed, ephemeral=True)

            
            log_channel = ctx.guild.get_channel(1163884909434253424)
            embed = discord.Embed(color=discord.Color.orange(), description=f'/give_item used')
            embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
            embed.add_field(name="Item bought:", value=f'{selected_item}', inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            await log_channel.send(embed=embed)  




    @bot.slash_command(description='Untraps a user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def untrap(self, ctx, user: Option(discord.Member, "The user you want to untrap")):
        try:
            print(1)
            db = sqlite3.connect("players.sqlite")
            cursor = db.cursor()

            cursor.execute(f"SELECT user FROM players WHERE user = {user.id} AND role = ? AND killed = 0", ("hunter",))
            print(2)
            alive = cursor.fetchone()
            print(alive)

            if alive:
                print("alive")
                cursor.execute("UPDATE players SET trapped = ? WHERE user =?", (0, user.id))

                embed = discord.Embed(color=discord.Color.orange(), description=f":chains::boom:︱You got freed from the trap!")
                embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                embed.timestamp = discord.utils.utcnow()
                embed.set_image(url="https://de.web.img3.acsta.net/r_654_368/newsv7/18/09/27/08/47/0998879.jpg")
                await user.send(f"{user.mention}", embed=embed)

                channel = ctx.guild.get_channel(1163909997126746223)
                print(channel)
                await channel.set_permissions(user, read_messages=True, send_messages=True)

                db.commit()
                cursor.close()
                db.close()

            if not alive:
                db.commit()
                cursor.close()
                db.close()
                return await ctx.respond(f"{user.mention} is dead or not participating in the game!")
        except Exception as e:
            await ctx.respond("exception", str(e))

                

    @bot.slash_command(description='Make a killed announcement about a user [admin]')
    @commands.guild_only()
    @discord.default_permissions(administrator = True)
    async def kill_announcement(self, ctx, user: Option(discord.Member, "The user you want to announce the death from")):
        channel = ctx.guild.get_channel(1163909997126746223)
        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
        embed.timestamp = discord.utils.utcnow()
        await channel.send("<@&961745027158122557>", embed=embed)


    @bot.command()
    async def day3(self, ctx):
        if ctx.author.id != 383115054431731726 and ctx.author.id != 192291195475591168 and ctx.author.id != 1152714944840749156:
            return
        
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"DELETE FROM players WHERE user = ?", ("killercooldown"))

        db.commit()
        cursor.close()
        db.close()


def setup(bot):
    bot.add_cog(Admin(bot))