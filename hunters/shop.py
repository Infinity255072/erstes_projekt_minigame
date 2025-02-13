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


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.slash_command(description="Buys an item from the shop")
    async def buy(self, ctx, item: Option(str, "Select the item you want to buy", choices=list(items.keys()))):
        selected_item = str(item)

        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()

        cursor.execute(f"SELECT user FROM players WHERE user = {ctx.author.id}")
        participant = cursor.fetchone()

        if not participant:
            await ctx.respond(":x:︱You are not participating in the game!", ephemeral=True)
        
            cursor.close()
            db.close()
            return

        if selected_item in items:
            cursor.execute(f"SELECT coins FROM currency WHERE user = {ctx.author.id}")
            coins = cursor.fetchone()
            coins = coins[0]
            
            price = items.get(item)

            if int(coins) < int(price):

                cursor.close()
                db.close()

                embed = discord.Embed(
                    color=discord.Color.red(),
                    description=f":x:︱You don't have enough coins to buy this item.")
                embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                                 icon_url=ctx.author.display_avatar)
                return await ctx.respond(embed=embed, ephemeral=True)

            cursor.execute("UPDATE currency SET coins = coins - ? WHERE user = ?", (price, ctx.author.id))
            db.commit()
            cursor.close()
            db.close()

            db = sqlite3.connect("players.sqlite")
            cursor = db.cursor()

            cursor.execute("SELECT * FROM items WHERE user =? AND item =?", (ctx.author.id, item))
            item_check = cursor.fetchone()

            embed = discord.Embed(description=f"You succesfully bought **1 {selected_item}** for **{price}** coins!",
                                  color=discord.Color.orange())
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            embed.timestamp = discord.utils.utcnow()

            if item_check:
                cursor.execute("UPDATE items SET amount = amount +1 WHERE user =? AND item = ?", (ctx.author.id, selected_item))
                db.commit()
                cursor.close()
                db.close()
                await ctx.respond(embed=embed, ephemeral=True)

            else:
                cursor.execute("INSERT INTO items VALUES (?, ?, 1)", (ctx.author.id, selected_item))
                db.commit()
                cursor.close()
                db.close()
                await ctx.respond(embed=embed, ephemeral=True)

            
            log_channel = ctx.guild.get_channel(1163884909434253424)
            embed = discord.Embed(color=discord.Color.orange(), description=f'Item bought')
            embed.add_field(name="Executed by:", value=f'{ctx.author.display_name}', inline=False)
            embed.add_field(name="Item bought:", value=f'{selected_item}', inline=False)
            embed.timestamp = discord.utils.utcnow()
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)
            await log_channel.send(embed=embed)  

       

    @bot.slash_command(description="Displays the shop")
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", color=discord.Color.orange(), description="Bento Box Shop")
        embed.add_field(name="Handgun", value=":coin: 7", inline=False)
        embed.add_field(name="Handgun ammo", value=":coin: 2", inline=False)
        embed.add_field(name="Rifle", value=":coin: 10", inline=False)
        embed.add_field(name="Rifle ammo", value=":coin: 3", inline=False)
        embed.add_field(name="Shotgun", value=":coin: 13", inline=False)
        embed.add_field(name="Shotgun ammo", value=":coin: 3", inline=False)
        embed.add_field(name="Bandage", value=":coin: 2", inline=False)
        embed.add_field(name="Medkit", value=":coin: 5", inline=False)

        await ctx.respond(embed=embed, ephemeral=True)


    @bot.slash_command(description="Displays your inventory")
    async def inventory(self, ctx):
        db = sqlite3.connect("players.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM items WHERE user = {ctx.author.id} AND amount > 0")
        result = cursor.fetchall()

        if not result:
            cursor.close()
            db.close()

            embed=discord.Embed(color=discord.Color.orange(), description="Your inventory is empty.")
            embed.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.display_avatar)
            return await ctx.respond(embed=embed, ephemeral=True)

        desc = ""

        for index, item in enumerate(result):
            desc += f"**{item[2]} - {item[1]}**\nㅤ\n"

            
        embed = discord.Embed(color=discord.Color.orange(), description=desc)
        embed.set_author(name=f"{ctx.author.name}'s Inventory", icon_url=ctx.author.display_avatar)
        embed.timestamp = discord.utils.utcnow()

        cursor.close()
        db.close()

        await ctx.respond(embed=embed, ephemeral=True)
        


def setup(bot):
    bot.add_cog(Shop(bot))