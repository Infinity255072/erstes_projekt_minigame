import discord
from discord.ext import commands
from discord.commands import Option
import sqlite3
import asyncio
import os
from discord.commands import slash_command, Option
from discord.utils import get


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)

hunters = []

class Revive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.slash_command(description="[Hunters] revive a dead hunter")
    @commands.cooldown(1, 172800, commands.BucketType.default) #only once every 2 days
    async def revive(self, ctx, hunter: Option(discord.Member, "The hunter you want to revive")):
        if ctx.author.id == hunter.id:
            self.revive.reset_cooldown(ctx)
            return await ctx.respond("You cant revive yourself!", ephemeral=True)
        hunters.clear()
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ? AND role = ? AND killed = 0 AND trapped = 0", (ctx.author.id, "hunter"))
        hunter_check = cursor.fetchone()

        cursor.execute(f"SELECT user FROM players WHERE user = ? AND killed = 1", (hunter.id,))
        killed = cursor.fetchone()

        if hunter_check and killed:
                hunters.clear()
                embed = discord.Embed(color=discord.Color.orange(), description=f':candle:︱{ctx.author.mention} is trying to revive {hunter.mention}! 4 hunters are needed to perform a ritual.')
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
                embed.timestamp = discord.utils.utcnow()
                embed.set_image(url="https://images.pond5.com/mysterious-ritual-skull-candles-and-footage-086481512_prevstill.jpeg")
                hunters.append(ctx.author.id)
                embed.add_field(name='Hunters:', value=len(hunters))
                await ctx.respond(embed=embed, view=ReviveView(hunter.id))

                log_channel = ctx.guild.get_channel(1163884909434253424)
                await log_channel.send(embed=embed)
        
        if not hunter_check:
            self.revive.reset_cooldown(ctx)
            cursor.close()
            db.close()

            return await ctx.respond(f"You are not a hunter or currently trapped!", ephemeral=True)
        
        if not killed:
            self.revive.reset_cooldown(ctx)
            cursor.close()
            db.close()

            return await ctx.respond(f"{hunter.mention} is not dead!", ephemeral=True)
    
        

def setup(bot):
    bot.add_cog(Revive(bot))
    


class ReviveView(discord.ui.View):
    def __init__(self, hunter_id):
        super().__init__(timeout=None)
        self.hunter_id = hunter_id

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.blurple, custom_id=f"revive_check")
    async def button_callback1(self, button: discord.Button, interaction: discord.Interaction):
        if interaction.user.id == self.hunter_id:
            return await interaction.response.send_message("You can't interact with that button!", ephemeral=True)
        message = interaction.message
        user = interaction.user

        if user.id not in hunters:
            hunters.append(user.id)
            await interaction.response.send_message(''':candle:︱You are now helping with the revival!''', ephemeral=True)

            db = sqlite3.connect("players.sqlite")
            cursor = db.cursor()

            embed = message.embeds[0]
            embed.clear_fields()
            embed.add_field(name='Hunters:', value=len(hunters))
            await message.edit(embed=embed)

            if len(hunters) == 4:
                button.disabled = True
                revived_hunter_id = self.hunter_id

                cursor.execute("UPDATE players SET killed = 0 WHERE user =?", (revived_hunter_id,))
                cursor.execute("UPDATE players SET health = 5 WHERE user =?", (revived_hunter_id,))

                db.commit()
                cursor.close()
                db.close()

                channel = interaction.guild.get_channel(1163909997126746223)
                user = interaction.guild.get_member(revived_hunter_id)
                await channel.set_permissions(user, read_messages=True, send_messages=True)
                voice_channel = interaction.guild.get_channel(1163910834456625273)
                await voice_channel.set_permissions(user, speak=True)

                embed = discord.Embed(color=discord.Color.orange(), description=f':candle:︱{user.mention} was successfully revived by {len(hunters)} hunters!')
                embed.set_author(name=f"{user.name}", icon_url=user.display_avatar)
                embed.set_image(url="https://images.pond5.com/mysterious-ritual-skull-candles-and-footage-086481512_prevstill.jpeg")
                embed.timestamp = discord.utils.utcnow()
                channel = interaction.guild.get_channel(1163909997126746223) 
                await channel.send("<@&961745027158122557>", embed=embed)

                log_channel = interaction.guild.get_channel(1163884909434253424)
                await log_channel.send(embed=embed)

                hunters.clear()

            if len(hunters) > 4:
                hunters.clear()
                await interaction.response.send_message(f''':candle:︱{user.mention} was already revived!''', ephemeral=True)


   
        elif user.id in hunters:
            await interaction.response.send_message(":x:︱You can't exit the ritual!", ephemeral=True)
