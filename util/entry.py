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


class Entry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS players(user INTEGER, role TEXT, health INTEGER, trapped INTEGER, killed INTEGER, clues INTEGER)")

        db.commit()
        cursor.close()
        db.close()

        self.bot.add_view(ParticipantView())


    @bot.command()
    @commands.guild_only()
    async def announcement(self, ctx):
        embed = discord.Embed(color=discord.Color.orange(), description=f"# Game Basis: \n - The game can have **1-3 Creatures** and the rest will be **Hunters.**\n"
            "- The goal for Hunters is to track and kill the Creature(s).\n"
            "- The Creature(s) try to **kill and trap Hunters** and **if all Hunters die, the Creature(s) win**.\n"
            "- Nobody, including the Creature, knows who the Creature is on the first day.\n"
            "- The Creatures are **randomly chosen** after the **first day.**\n"
            "- The Creature can choose to **reveal themselves** or **remain stealthy.**\n"
            "- Nobody will know how the clues will look like until found.\n"
            "- Special **currency** for buying items.\n"
            "- Hunters will be able to free themselves and can also perform a ritual to bring back dead hunters.\n\nInteract with the button below to take place in the game!")
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url)
        embed.timestamp = discord.utils.utcnow()

        embed.add_field(name='Participants:', value=get_participants(ctx.guild))

        await ctx.channel.purge(limit=1)
        channel = ctx.guild.get_channel(1163909997126746223)
        await channel.send("<@&961745027158122557>", embed=embed, view=ParticipantView())

        

def setup(bot):
    bot.add_cog(Entry(bot))

def get_participants(guild):
    db = sqlite3.connect("players.sqlite")
    cursor = db.cursor()
    
    participants = 0
    
    for member in guild.members:
        cursor.execute(f"SELECT user FROM players WHERE user = ?", (member.id,))
        participant = cursor.fetchone()

        if participant:
            participants += 1

    db.commit()
    cursor.close()
    db.close()

    return participants

    
        
    



class ParticipantView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.blurple, custom_id="participants_check")
    async def button_callback1(self, button, interaction: discord.Interaction):

        message = interaction.message
        user = interaction.user
        
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = ?", (user.id,))
        participant = cursor.fetchone()

        if not participant:
            cursor.execute("INSERT INTO players(user, health, trapped, killed) VALUES (?, ?, ?, ?)", (user.id, 0, 0, 0,))

            await interaction.response.send_message('''✅︱You are now taking part in the game! If you don't want to participate anymore, press the button again!''', ephemeral=True)

        
        cursor.execute(f"SELECT user FROM currency WHERE user = {user.id}")
        result = cursor.fetchone()


        if result is None:
            cursor.execute("INSERT INTO currency(user, coins) VALUES (?, ?)", (user.id, 0))
            
    
        if participant:
            cursor.execute(f"DELETE FROM players WHERE user = ?", (user.id,))

            if result:
                cursor.execute(f"DELETE FROM currency WHERE user = ?", (user.id,))

            await interaction.response.send_message('''✅︱You are no longer participating in the game!''', ephemeral=True)

        
        db.commit()
        cursor.close()
        db.close()

        embed = message.embeds[0]
        embed.clear_fields()
        embed.add_field(name='Participants:', value=get_participants(interaction.guild))
        await message.edit(embed=embed)

        