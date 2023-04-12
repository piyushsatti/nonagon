from email.message import Message
import discord
from discord.ext import commands

# Code Imports
from cog_base_class import Base

# Dataclasses import
from reaction_roles_dataclass import ReactionRole

class ReactionRolesCog(Base, name="ReactionRolesCog"):
    """Enables you to create your own reaction roles"""
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command()
    async def set_reaction_roles(self, ctx:commands.Context):
        '''Sets up reaction roles'''
        
        def check(message: discord.Message):
                return message.author == ctx.author
        
        try:
            if (await self.cog_status("ReactionRolesCog", ctx.guild.id)) == True:
                await ctx.send(
                    content="Please tag the appropriate channel =>"
                )
                reaction_roles_channel_mentions: discord.Message = (
                    await self.bot.wait_for('message', timeout=60, check=check)
                )
                await ctx.send(
                    content="Please type the message content =>"
                )
                reaction_roles_message_content:discord.Message = (
                    await self.bot.wait_for('message', timeout=60, check=check)
                )
                await ctx.send(
                    content="Please mentions the embed like =>\ntitle=...\ndescription=...\ntitle=...\ndescription=...\n...\n\nType anything else to skip"
                )
                reaction_role_message_embeds:discord.Message = (
                    await self.bot.wait_for('message', timeout=60.0, check=check)
                )
                await ctx.send(
                    content="Please mention the emoji and role as =>\n `emoji @role`\n`emoji @role`\n..."
                )
                reaction_role_map_message: discord.Message = (
                    await self.bot.wait_for('message', timeout=60.0, check=check)
                )
                embed_list = []
                # Embed processing
                embed_list_text_raw = reaction_role_message_embeds.content.split('\n')
                for i, ele in enumerate(embed_list_text_raw):
                    if i%2:
                        pass
                    else:
                        if ele.strip().startswith("title"):
                            embed_list.append({
                                'title':embed_list_text_raw[i].replace("title=",""),
                                'description':embed_list_text_raw[i+1].replace("description=","")
                            })
                # send the main message and add the reactions
                main_message_obj:discord.Message = await reaction_roles_channel_mentions.channel_mentions[0].send(
                    content=reaction_roles_message_content.content,
                    embeds=[
                        discord.Embed(
                            color=self.bot.color, 
                            title=ele["title"], 
                            description=ele["description"]
                        ) 
                    for ele in embed_list]
                )
                reaction_role_map_list = {}
                for ele in reaction_role_map_message.content.split('\n'):
                    tmp = ele.split(' ', 1)
                    role_id = tmp[1][3:-1]
                    reaction_id = tmp[0]
                    reaction_role_map_list[f'{role_id}'] = reaction_id
                for key in reaction_role_map_list:
                    await main_message_obj.add_reaction(reaction_role_map_list[key])
                t = ReactionRole()
                t.guild_id = ctx.guild.id
                t.load()
                # json(message_id -> [channel_id, message_content, embed->[title, description], role_id -> reaction_id])
                t.message_role_reaction_map[f"{main_message_obj.id}"] = [
                    f"{reaction_roles_channel_mentions.channel_mentions[0].id}",
                    reaction_roles_message_content.content,
                    {'embed':embed_list},
                    reaction_role_map_list
                ]
                t.update()
        except TimeoutError:
            await ctx.send("Request Timed Out. Try again.")
        except Exception as e:
            print(f"--- Exception in set_reaction_roles ---\n{e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent):
        try:
            if payload.member.bot: 
                return
            t = ReactionRole()
            t.guild_id = str(payload.guild_id)
            t.load()
            if str(payload.message_id) in t.message_role_reaction_map.keys():
                reaction_map:dict = t.message_role_reaction_map[str(payload.message_id)][3]
                guild_obj = self.bot.get_guild(payload.guild_id)
                for key, val in reaction_map.items():
                    if val == str(payload.emoji):
                        await payload.member.add_roles(
                            guild_obj.get_role(int(key))
                        )
                        break
        except Exception as e:
            print(f"--- Exception in on_raw_reaction_add ---\n{e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
        try:
            t = ReactionRole()
            t.guild_id = str(payload.guild_id)
            t.load()
            if str(payload.message_id) in t.message_role_reaction_map.keys():
                reaction_map:dict = t.message_role_reaction_map[str(payload.message_id)][3]
                guild_obj:discord.Guild = self.bot.get_guild(payload.guild_id)
                member_obj:discord.Member = guild_obj.get_member(payload.user_id)
                for key, val in reaction_map.items():
                    if val == str(payload.emoji):
                        await member_obj.remove_roles(
                            guild_obj.get_role(int(key))
                        )
                        break
        except Exception as e:
            print(f"--- Exception in on_raw_reaction_remove ---\n{e}")

async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))