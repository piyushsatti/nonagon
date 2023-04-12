from dis import disco
import discord
from asyncio import sleep
from discord.ext import commands, tasks

# Code Imports
from cog_base_class import Base
from ticket_dataclass import TicketDataclass

class Tickets(Base, name="TicketsCog"):
    """Lets you create tickets"""
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command()
    async def set_ticket(self, ctx:commands.Context, channel:discord.TextChannel):
        
        def check(m:discord.Message):
            return m.author == ctx.author
        
        try:
            '''Allows setting up of tickets'''
            await ctx.send(
                content="Input the title and the description of the ticket (Title | Description)"
            ) 
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            title, desc = msg.content.split("|")
            await ctx.send(
                content="Please input the name of the category you'd like new tickets to be in"
            )
            category = await self.bot.wait_for('message', timeout=60.0, check=check)
            category_id = (discord.utils.get(ctx.guild.categories, name=category.content)).id
            msg = await channel.send(
                embed=discord.Embed(
                    title=title.strip(), 
                    description=desc.strip(),
                    color=self.bot.color
                )
            )
            await msg.add_reaction("📧")
            t = TicketDataclass()
            t.guild_id = ctx.guild.id
            t.load()
            # json('message_id' -> [title, desc, channel_id, category_id, message_id->ticket_ids])
            t.message_to_ticket_map[f"{msg.id}"] = [
                title,
                desc,
                str(ctx.channel.id),
                str(category_id),
                {}
            ]
            t.update()
        except Exception as e:
            raise Exception(f"--- Exception in set_ticket ---\n{e}")
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent):
        try:
            if payload.member.bot: 
                return
            guild_obj:discord.Guild = self.bot.get_guild(payload.guild_id)
            member_obj:discord.Member = guild_obj.get_member(payload.user_id)
            t = TicketDataclass()
            t.guild_id = payload.guild_id
            t.load()
            if str(payload.emoji) == "📧" and str(payload.message_id) in t.message_to_ticket_map.keys():
                category_obj:discord.CategoryChannel = discord.utils.get(
                    guild_obj.categories, 
                    id=int(t.message_to_ticket_map[str(payload.message_id)][3])
                )
                overwrites = {
                    payload.member.guild.default_role:discord.PermissionOverwrite(
                        read_messages=False,
                        send_messages=False,
                    ),
                    payload.member:discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                    )
                }
                channel_obj:discord.TextChannel = await category_obj.create_text_channel(name=f'ticket-{payload.user_id}', overwrites=overwrites)
                main_msg:discord.Message = await channel_obj.send(embed=discord.Embed(title="Your ticket", description='React with 🔐 to close.'))
                await main_msg.add_reaction("🔐")
                t.message_to_ticket_map[str(payload.message_id)][4][f'{channel_obj.id}'] = f'{main_msg.id}'
                t.update()
            if str(payload.emoji) == "🔐":
                for key in t.message_to_ticket_map.keys():
                    if str(payload.message_id) in t.message_to_ticket_map[key][4].values():
                        channel_obj = discord.utils.get(guild_obj.channels, id=payload.channel_id)
                        await channel_obj.send(
                            embed=discord.Embed(
                                title="Deleting channel in 5 seconds...", 
                                color=self.bot.color
                            )
                        )
                        await sleep(5)
                        await channel_obj.delete()
                        t.message_to_ticket_map[key][4].pop(str(payload.message_id))
                        break
        except Exception as e:
            raise Exception(f"--- Exception in on_raw_reaction_add ---\n{e}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))