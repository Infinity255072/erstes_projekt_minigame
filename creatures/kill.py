import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
import asyncio
from discord.commands import slash_command, Option
from discord.utils import get


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)



class Kill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="[Creature] kills a hunter")
    @commands.cooldown(1, 86400, commands.BucketType.user) #only once per day
    async def kill(self, ctx: discord.ApplicationContext, hunter: Option(discord.Member, "The hunter you want to kill")):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id} AND role = ?", ("creature",))
        creature = cursor.fetchone()

        cursor.execute(f"SELECT user FROM players WHERE user = ?", ("killercooldown",))
        cooldown = cursor.fetchone()

        if creature and cooldown:
            self.kill.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You cant use this command today!', ephemeral=True)
    
        if creature:
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

                embed = discord.Embed(color=discord.Color.red(), description=f":knife::drop_of_blood:︱You got killed by the creature! Please keep in mind that you are not allowed to talk about the game anymore in any channel as you're no longer participating in the game!")
                embed.set_author(name=f"{hunter.name}", icon_url=hunter.display_avatar)
                embed.timestamp = discord.utils.utcnow()
                embed.set_image(url="https://i0.wp.com/popwire.net/wp-content/uploads/2021/06/universal-halloween-kills-official-trailer.jpg?fit=593%2C310&ssl=1")
                await hunter.send(embed=embed)

                log_channel = ctx.guild.get_channel(1163884909434253424)
                embed = discord.Embed(color=discord.Color.orange(), description=f'Command `/kill` used')
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
            


        if not creature:
            self.kill.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You are not the creature!', ephemeral=True)
        
        if cooldown:
            self.trap.reset_cooldown(ctx)
            cursor.close()
            db.close()
            return await ctx.respond('You cant use this command today!', ephemeral=True)
        





def setup(bot):
    bot.add_cog(Kill(bot))