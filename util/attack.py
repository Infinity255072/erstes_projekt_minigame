import discord
from discord.ext import commands, tasks
from discord.commands import Option
import sqlite3
from discord.commands import slash_command, Option
from discord.utils import get
import random
import asyncio
from datetime import time, timezone


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Attack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        self.dead_hunters_check.start()

    @tasks.loop(seconds=60)
    async def dead_hunters_check(self):
        guild = self.bot.get_guild(843116027219148810)

        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ? AND clues = ?", ("day", "2"))
        day2 = cursor.fetchone()

        if not day2:
             return

        count = 0
        for member in guild.members:
            cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 0 AND role = ?", (member.id, 'hunter'))
            hunter = cursor.fetchone()
  

            if hunter:
                 count += 1
        
        if count == 0:
            channel = guild.get_channel(1163909997126746223)
            embed = discord.Embed(color=discord.Color.orange(), description=f'All hunters were successfully killed! :skull_crossbones: The game is now over.')
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url="https://media.gq-magazin.de/photos/617283913f79fd7c589247ec/16:9/w_2560%2Cc_limit/Halloween%2520Kills.jpg")
            await channel.send("<@&961745027158122557>",embed=embed)

            log_channel = guild.get_channel(1163884909434253424)
            embed = discord.Embed(color=discord.Color.orange(), description=f'All hunters were succesfully killed by the creature! The game is now over.')
            embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=embed)

            cursor.execute(f"DELETE FROM players WHERE user = ?", ("day",))

            db.commit()
            cursor.close()
            db.close()

            print(123)
            return
        
        db.commit()
        cursor.close()
        db.close()


    @bot.slash_command(description="Attack someone")
    @commands.cooldown(1, 10800, commands.BucketType.user) #only once every 3 hours
    async def attack(self, ctx, item: Option(str, "Select the item you want to attack with", choices=["Knife", "Handgun", "Rifle", "Shotgun", "Claws [Creature]"]), user: Option(discord.Member, "The user you want to attack")):
        selected_item = str(item)

        if int(user.id) == int(ctx.author.id):
            self.attack.reset_cooldown(ctx)
            return await ctx.respond(f":x:︱You can't attack yourself, {ctx.author.mention}!", ephemeral=True)
        
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ?", ("killercooldown",))
        cooldown = cursor.fetchone()

        cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 0", (ctx.author.id,))
        participant = cursor.fetchone()

        cursor.execute(f"SELECT user FROM players WHERE role = ? AND user = ?", ("creature", ctx.author.id))
        creature = cursor.fetchone()
        creature_id = int(creature[0])

        if creature and cooldown:
            self.attack.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You cant use that command today!', ephemeral=True)

        if not participant:
            await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)

            cursor.close()
            db.close()
            self.attack.reset_cooldown(ctx)
            return
        
        cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 0", (user.id,))
        participant = cursor.fetchone()

        if not participant:
            self.attack.reset_cooldown(ctx)
            await ctx.respond(f":x:︱ {user.mention} is not participating in the game!", ephemeral=True)

            cursor.close()
            db.close()
            return
        
        cursor.execute("SELECT item FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, selected_item))
        item = cursor.fetchone()

        if not item and selected_item != "Claws [Creature]":
            self.attack.reset_cooldown(ctx)
            return await ctx.respond(f":x:︱You don't have a {selected_item.lower()}!", ephemeral=True)


        if selected_item == "Handgun":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Handgun ammo'))
                hg_ammo = cursor.fetchone()

                if not hg_ammo:
                    self.attack.reset_cooldown(ctx)
                    return await ctx.respond(":x:︱You don't have enough ammo to use that gun!", ephemeral=True)

                if hg_ammo:
                    cursor.execute("UPDATE items SET amount = amount -1 WHERE user =? AND item = ?", (ctx.author.id, "Handgun ammo"))
                    cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
                    health = cursor.fetchone()
                    health = int(health[0])

                    if health >= 3:
                        cursor.execute("UPDATE players SET health = health -2 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with a Handgun! You used 1 Handgun ammo.' , ephemeral = True)
                        
                        embed = discord.Embed(color=discord.Color.red(), description=f':drop_of_blood:︱You got attacked and lost **2** health points!')
                        embed.timestamp = discord.utils.utcnow()
                        await user.send(f'user.mention', embed=embed)

                    if health <= 2:
                        cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, user.id))

                        embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {user.mention}, as this was their last health!')
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                
                        await ctx.respond(embed=embed, ephemeral=True)

                        embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by an unknown person! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                        await user.send(embed=embed)

                        cursor.execute("UPDATE players SET health = 0 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        channel = ctx.guild.get_channel(1163909997126746223)
                        await channel.set_permissions(user, read_messages=True, send_messages=False)
                        voice_channel = ctx.guild.get_channel(1163910834456625273)
                        await voice_channel.set_permissions(user, speak=False)

                        channel = ctx.guild.get_channel(1163909997126746223)
                        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        await asyncio.sleep(1800)
                        await channel.send("<@&961745027158122557>", embed=embed)

                    
        if selected_item == "Rifle":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Rifle ammo'))
                rfle_ammo = cursor.fetchone()

                if not rfle_ammo:
                    self.attack.reset_cooldown(ctx)
                    await ctx.respond(":x:︱You don't have enough ammo to use that gun!", ephemeral=True)
                    return

                if rfle_ammo:
                    cursor.execute("UPDATE items SET amount = amount -1 WHERE user =? AND item = ?", (ctx.author.id, "Rifle ammo"))
                    cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
                    health = cursor.fetchone()
                    health = int(health[0])

                    if health >= 4:
                        cursor.execute("UPDATE players SET health = health -3 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with a Rifle! You used 1 Rifle ammo.', ephemeral = True)
                        
                        embed = discord.Embed(color=discord.Color.red(), description=f':drop_of_blood:︱You got attacked and lost **3** health points!')
                        embed.timestamp = discord.utils.utcnow()
                        await user.send(f'{user.mention}', embed=embed)

                    if health <= 3:
                        cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, user.id))

                        embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {user.mention}, as this was their last health!')
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                
                        await ctx.respond(embed=embed, ephemeral=True)

                        embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by an unknown person! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                        await user.send(embed=embed)

                        cursor.execute("UPDATE players SET health = 0 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        channel = ctx.guild.get_channel(1163909997126746223)
                        await channel.set_permissions(user, read_messages=True, send_messages=False)
                        voice_channel = ctx.guild.get_channel(1163910834456625273)
                        await voice_channel.set_permissions(user, speak=False)

                        channel = ctx.guild.get_channel(1163909997126746223)
                        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        await asyncio.sleep(1800)
                        await channel.send("<@&961745027158122557>", embed=embed)
                    

        if selected_item == "Shotgun":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Shotgun ammo'))
                sg_ammo = cursor.fetchone()

                if not sg_ammo:
                    self.attack.reset_cooldown(ctx)
                    return await ctx.respond(":x:︱You don't have enough ammo to use that gun!", ephemeral=True)

                if sg_ammo:
                    cursor.execute("UPDATE items SET amount = amount -1 WHERE user =? AND item = ?", (ctx.author.id, "Shotgun ammo"))
                    cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
                    health = cursor.fetchone()
                    health = int(health[0])

                    if health >= 6:
                        cursor.execute("UPDATE players SET health = health -5 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with a Handgun! You used 1 Shotgun ammo.', ephemeral = True)
                        
                        embed = discord.Embed(color=discord.Color.red(), description=f':drop_of_blood:︱You got attacked and lost **5** health points!')
                        embed.timestamp = discord.utils.utcnow()
                        await user.send(f'{user.mention}', embed=embed)

                    if health <= 5:
                        cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, user.id))

                        embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {user.mention}, as this was their last health!')
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                
                        await ctx.respond(embed=embed, ephemeral=True)

                        embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by an unknown person! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                        await user.send(embed=embed)

                        cursor.execute("UPDATE players SET health = 0 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        channel = ctx.guild.get_channel(1163909997126746223)
                        await channel.set_permissions(user, read_messages=True, send_messages=False)
                        voice_channel = ctx.guild.get_channel(1163910834456625273)
                        await voice_channel.set_permissions(user, speak=False)

                        channel = ctx.guild.get_channel(1163909997126746223)
                        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        await asyncio.sleep(1800)
                        await channel.send("<@&961745027158122557>", embed=embed)


        if selected_item == "Knife":
                cursor.execute("SELECT * FROM items WHERE user =? AND item =? AND amount > 0", (ctx.author.id, 'Knife'))
                knife = cursor.fetchone()
        
                if not knife:
                    self.attack.reset_cooldown(ctx)
                    return await ctx.respond(":x:︱You don't have a knife!", ephemeral=True)

                chance = random.random()
                damage = 1

                if chance <= 0.1:
                    damage = 3

                if knife:
                    cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
                    health = cursor.fetchone()
                    health = int(health[0])

                    if health >= damage + 1:
                        cursor.execute("UPDATE players SET health = health -? WHERE user =?", (damage, user.id))

                        db.commit()
                        cursor.close()
                        db.close()

                        if damage == 1:
                            await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with a Knife! {user.mention} lost {damage} health points.', ephemeral=True)

                        if damage == 3:
                            await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with a Knife and made critical damage. {user.mention} lost {damage} health points!', ephemeral=True)
                        
                        embed = discord.Embed(color=discord.Color.red(), description=f':drop_of_blood:︱You got attacked and lost **{damage}** health points!')
                        embed.timestamp = discord.utils.utcnow()
                        await user.send(f'{user.mention}', embed=embed)

                    if health <= damage:
                        cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, user.id))

                        embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {user.mention}, as this was their last health!')
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                
                        await ctx.respond(embed=embed, ephemeral=True)

                        embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by an unknown person! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                        await user.send(embed=embed)

                        channel = ctx.guild.get_channel(1163909997126746223)
                        await channel.set_permissions(user, read_messages=True, send_messages=False)
                        voice_channel = ctx.guild.get_channel(1163910834456625273)
                        await voice_channel.set_permissions(user, speak=False)

                        cursor.execute("UPDATE players SET health = 0 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        channel = ctx.guild.get_channel(1163909997126746223)
                        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        await asyncio.sleep(1800)
                        await channel.send("<@&961745027158122557>", embed=embed)


        if selected_item == "Claws [Creature]":
                cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("creature",))
                creature = cursor.fetchone()
        
                if not creature:
                    self.attack.reset_cooldown(ctx)
                    return await ctx.respond(":x:︱You are not the creature!", ephemeral=True)



                if creature:
                    cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
                    health = cursor.fetchone()
                    health = int(health[0])

                    if health >= 3:
                        cursor.execute("UPDATE players SET health = health -2 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        await ctx.respond(f':knife:︱You succesfully attacked {user.mention} with you claw! {user.mention} lost 2 health points!', ephemeral=True)
                        
                        embed = discord.Embed(color=discord.Color.red(), description=f':drop_of_blood:︱You got attacked and lost **2** health points!')
                        embed.timestamp = discord.utils.utcnow()
                        await user.send(f'{user.mention}', embed=embed)
                        

                    if health <= 2:
                        cursor.execute("UPDATE players SET killed = ? WHERE user =?", (1, user.id))

                        embed = discord.Embed(color=discord.Color.orange(), description=f':knife::drop_of_blood:︱You succesfully killed {user.mention}, as this was their last health!')
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                
                        await ctx.respond(embed=embed, ephemeral=True)

                        embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by an unknown person! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                        await user.send(embed=embed)

                        channel = ctx.guild.get_channel(1163909997126746223)
                        await channel.set_permissions(user, read_messages=True, send_messages=False)
                        voice_channel = ctx.guild.get_channel(1163910834456625273)
                        await voice_channel.set_permissions(user, speak=False)

                        cursor.execute("UPDATE players SET health = 0 WHERE user =?", (user.id,))

                        db.commit()
                        cursor.close()
                        db.close()

                        channel = ctx.guild.get_channel(1163909997126746223)
                        embed = discord.Embed(color=discord.Color.red(), description=f"{user.mention} was found dead! Their cause of death is currently unknown.")
                        embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                        embed.timestamp = discord.utils.utcnow()
                        await asyncio.sleep(1800)
                        await channel.send("<@&961745027158122557>", embed=embed)

            


        log_channel = ctx.guild.get_channel(1163884909434253424)
        embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/attack` used')
        embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
        embed.add_field(name="Used on:", value=f'{user.display_name}', inline=False)
        embed.add_field(name="Weapon:", value=f'{selected_item}', inline=False)
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
        await log_channel.send(embed=embed)
        print("sent")

        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT health FROM players WHERE user = {user.id}")
        health = cursor.fetchone()
        health = int(health[0])
        
        cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 1 AND role = ?", (user.id, 'creature'))
        creature = cursor.fetchone()
        try:
            creature = int(creature[0])
        except:
             creature = 0


        if user.id == creature:
            channel = ctx.guild.get_channel(1163909997126746223)
            embed = discord.Embed(color=discord.Color.orange(), description=f'The creature was succesfully killed by {ctx.author.mention}! :tada: The game is now over.')
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url="https://i0.wp.com/www.tor.com/wp-content/uploads/2021/10/halloween-kills-mob.jpg?resize=740%2C341&type=vertical&ssl=1")
            await channel.send("<@&961745027158122557>",embed=embed)

            log_channel = ctx.guild.get_channel(1163884909434253424)
            embed = discord.Embed(color=discord.Color.orange(), description=f'The creature was killed by {ctx.author.name}! The game is now over.')
            embed.add_field(name="Weapon:", value=f'{selected_item}', inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            await log_channel.send(embed=embed)
            return
        
    
             
             

        







def setup(bot):
    bot.add_cog(Attack(bot))