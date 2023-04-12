import discord, asyncio, sys, json
from discord.ext import commands

# Code Imports
from cog_base_class import Base

# dataclasses import
from guild_data_dataclass import GuildData
from welcome_messages_dataclass import WelcomeMessages

class Mod(Base, name="ModerationCog"):
    """Commands for server moderators"""
    def __init__(self, bot):
        super().__init__(bot)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, prefix):
        '''Sets the bot's prefix for the guild.'''
        try:
            t = GuildData()
            t.guild_id = ctx.guild.id
            t.load()
            t.guild_prefix = prefix
            t.update()
            await ctx.send(f"Prefix changed tp: {prefix}")
        except Exception as e:
            raise Exception(f"--- Exception in setprefix ---\n{e}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        '''Kicks the user'''
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                color = self.bot.color,
                title = f"{member.name} has been kicked."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in kick ---\n{e}")
        
    
    @commands.command()
    @commands.has_permissions(ban_members=True) 
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        '''Bans the user'''
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                color = self.bot.color,
                title = f"{member.name} has been banned."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in ban ---\n{e}")

    @commands.command()
    @commands.has_permissions(ban_members=True) 
    async def unban(self, ctx, user_id : int):
        '''Unbans the user'''
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(
                color = self.bot.color,
                title = f"{user.name} has been banned."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in unban ---\n{e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member : discord.Member, days, reason=None):
        '''Bans the user for the given number of days'''
        try:
            days * 5 
            await member.ban(reason=reason)
            embed = discord.Embed(
                color = self.bot.color,
                title = f"{member.name} has been soft-banned for {days} days."
            )
            await ctx.send(embed=embed)
            await asyncio.sleep(days)
        except Exception as e:
            raise Exception(f"--- Exception in softban ---\n{e}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        try:
            t = WelcomeMessages()
            t.guild_id = ctx.guild.id
            t.load()
            t.channel_id = str(channel.id)
            t.update()
            await ctx.send(f"Updated welcome channel to {channel.mention}!")
        except Exception as e:
            raise Exception(f"--- Exception in setwelcome ---\n{e}")

async def setup(bot):
    await bot.add_cog(Mod(bot))