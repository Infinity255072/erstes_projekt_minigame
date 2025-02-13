import discord
from discord.ext import commands
from discord.commands import Option
from discord.commands import slash_command, Option
from discord.utils import get


allowed_mentions = discord.AllowedMentions(everyone = True)


bot = commands.Bot(case_insensitive=True)


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        channel = ctx.guild.get_channel(1163884909434253424)
        embed = discord.Embed(title="Error", description=f"An error occured while trying to execute `{ctx.message.content}` from {ctx.author.display_name} in <#{ctx.channel.id}>!\n\Reason: ```{error}```\nㅤ\n", color=discord.Color.brand_red())
        embed.add_field(name="Traceback", value=f"```{error}```")
        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)
        if isinstance(error, commands.CommandError):
            await ctx.send(f"<@1152714944840749156> {error}")
            raise error
        raise error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        channel = ctx.guild.get_channel(1163884909434253424)
        embed = discord.Embed(title="Error", description=f"An error occured while trying to execute `{ctx.message.content}` from {ctx.author.display_name} in <#{ctx.channel.id}>!\n\Reason: ```{error}```\nㅤ\n", color=discord.Color.brand_red())
        embed.add_field(name="Traceback", value=f"```{error}```")
        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)
        if isinstance(error, TypeError):
            await ctx.send(f"<@1152714944840749156> {error}")
            raise error
        raise error

    
    @staticmethod
    def convert_time(seconds):
        if seconds < 60:
            return f"{round(seconds)} seconds"
        elif seconds < 3600: 
            minutes = seconds / 60
            return f"{round(minutes)} minutes"
        else:
            hours = seconds / 3600
            return f"{round(hours)} hours"
        
    
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = ctx.command.get_cooldown_retry_after(ctx)
            final_time = self.convert_time(seconds)
            embed = discord.Embed(description=f"You need to wait {final_time} until you can use this command again!", color=discord.Color.orange())
            embed.timestamp = discord.utils.utcnow()
            await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Error(bot))