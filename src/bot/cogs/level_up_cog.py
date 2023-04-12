from multiprocessing import context
from turtle import update
import discord, asyncio
from datetime import datetime, timedelta
from random import randint
from discord.ext import commands
from discord import Member
from typing import Optional

# Code Imports
from cog_base_class import Base
from peppermint_bot import get_prefix

# dataclasses import
from level_up_dataclass import LevelUp

class Levels(Base, name="LevelUpCog"):
    """The Levelling/XP system"""
    def __init__(self, bot):
        super().__init__(bot)

    async def update_invites(self, guild_id:str, member_id:str, increment:bool=True):
        t = LevelUp()
        t.guild_id = guild_id
        t.load()
        if increment:
            t.user_data[member_id]['invites'] += 1
        else:
            t.user_data[member_id]['invites'] -= 1
        t.update()

    async def process_xp(self, message:discord.Message):
        guild_id = str(message.guild.id)
        member_id = str(message.author.id)
        t = LevelUp()
        t.guild_id = guild_id
        t.load()
        if datetime.utcnow() > datetime.fromisoformat(t.user_data[member_id]['xp_lock']):
            xp = t.user_data[member_id]['xp']
            old_lvl = int(((xp)//42) ** 0.55)
            xp_to_add = randint(10, 20)
            new_lvl = int(((xp+xp_to_add)//42) ** 0.55)
            if new_lvl > old_lvl:
                embed = discord.Embed(
                    color = self.bot.color,
                    description = f"Congrats {message.author.mention} - you reached level {new_lvl}!"
                )
                await message.channel.send(embed=embed)
            t.user_data[member_id]['xp'] = xp + xp_to_add
            t.user_data[member_id]['xp_lock'] = (datetime.utcnow()+timedelta(seconds=1)).isoformat()
            t.update()

    @commands.command()
    async def display_level(self, ctx:commands.Context, target: Optional[Member]= None):
        '''Shows the user's level'''
        try:
            if (await self.cog_status("LevelUp", ctx.guild.id)) == True:
                if target is not None:
                    target = target
                else:
                    target = ctx.member
                t = LevelUp()
                t.guild_id = ctx.guild.id
                t.load()
                xp = t.user_data[target.id]['xp']
                embed = discord.Embed(
                    color = self.bot.color,
                    title = f"{target.display_name} is on level {int(((xp)//42) ** 0.55):,} with {xp:,} XP."
                )
                await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in display_level ---\n{e}")

    @commands.command()
    async def leaderboard(self, ctx:commands.Context):
        '''Displays the top 50 members sorted by XP'''
        try:
            if (await self.cog_status("LevelUp", ctx.guild.id)) == True:
                buttons = {}
                for i in range(1, 6): 
                    buttons[f"{i}\N{COMBINING ENCLOSING KEYCAP}"] = i 
                previous_page = 0
                current = 1
                index = 1
                entries_per_page = 10
                embed = discord.Embed(title=f"Leaderboard Page {current}", description="", colour=self.bot.color)
                msg = await ctx.send(embed=embed)
                for button in buttons:
                    await msg.add_reaction(button)
                ###
                t = LevelUp()
                t.guild_id = ctx.guild.id
                t.load()
                user_data = t.user_data
                members_sorted_by_xp = sorted(user_data.items(), key=lambda user_data: user_data[1]["xp"])
                ###
                while True:
                    if current != previous_page:
                        embed.title = f"Leaderboard Page {current}"
                        embed.description = ""
                        ###
                        index_start = entries_per_page*(current-1)
                        index_end = entries_per_page*(current)
                        page_data = members_sorted_by_xp[index_start:index_end]
                        ###
                        async for entry in page_data:
                            index += 1
                            member_id = entry[0]
                            exp = entry[1]["xp"]
                            member = ctx.guild.get_member(int(member_id))
                            embed.description += f"{index}) {member.mention} : {exp}\n"
                        await msg.edit(embed=embed)
                        try:
                            reaction, _ = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)
                        except asyncio.TimeoutError:
                            return await msg.clear_reactions()
                    else:
                        previous_page = current
                        await msg.remove_reaction(reaction.emoji, ctx.author)
                        current = buttons[reaction.emoji]
        except Exception as e:
            raise Exception(f"--- Exception in leaderboard ---\n{e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.bot.tracker.fetch_inviter(member)
        await self.update_invites(member.guild.id, inviter.id, True)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        inviter = await self.bot.tracker.fetch_inviter(member)
        await self.update_invites(member.guild.id, inviter.id, False)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        try:
            if (await self.cog_status("LevelUpCog", message.guild.id)) == True:
                if not message.author.bot:
                    msg: str = message.content
                    prefix: str = (await get_prefix(self.bot, message))
                    if msg.startswith(prefix):
                        t = LevelUp()
                        t.guild_id = message.guild.id
                        t.load()
                        if message.author.id not in t.user_data.keys():
                            t.user_data[str(message.author.id)] =  {'xp': 0, 'invites': 0, 'xp_lock': datetime.utcnow().isoformat()}
                            t.update()
                        else:
                            await self.process_xp(message)
        except Exception as e:
            raise Exception(f"--- Exception in on_message level_up cog ---\n{e}")

async def setup(bot):
    await bot.add_cog(Levels(bot))