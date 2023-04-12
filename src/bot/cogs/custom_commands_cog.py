from email import message
import discord
from discord.ext import commands

# Code Imports
from cog_base_class import Base
from peppermint_bot import get_prefix

# Dataclasses Imports
from custom_commands_dataclass import CustomCommands

class CustomCommandsCog(Base, name="CustomCommandsCog"):
    """Lets you create your own custom commands"""
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command()
    async def set_command(self, ctx:commands.Context, command:str, *, msg:str):
        '''Create a new custom command'''
        try:
            t = CustomCommands()
            t.guild_id = ctx.guild.id
            t.load()
            t.command_name_to_message_map[f'{command}'] = msg
            t.update()
            embed = discord.Embed(
                color = self.bot.color,
                title = f"Custom Command `{command}` now refers to `{msg}`."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in set_command ---\n{e}")

    @commands.command()
    async def delete_custom_command(self, ctx:commands.Context, command_name:str):
        '''Deletes a custom command'''
        try:
            t = CustomCommands()
            t.guild_id = ctx.guild.id
            t.load()
            popped_command = t.command_name_to_message_map.pop(f'{command_name}')
            t.update()
            embed = discord.Embed(
                color = self.bot.color,
                title = f"Custom Command `{popped_command}` has been deleted."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in delete_custom_command ---\n{e}")
   
    @commands.command()
    async def list_custom_commands(self, ctx:commands.Context):
        '''Lists all the custom commands created'''
        try:
            t = CustomCommands()
            t.guild_id = ctx.guild.id
            t.load()
            if not len(t.command_name_to_message_map):
                await ctx.send(
                    content="No custom command exists for this server."
                )
                return
            else:
                embed = discord.Embed(
                    color = self.bot.color,
                    title = f"All custom commands for {ctx.guild.name}\n"
                )
                for key, val in t.command_name_to_message_map.items():
                    embed.add_field(name=key, value=f"```{val}```", inline=True)
                await ctx.send(embed=embed)
        except Exception as e:
            raise Exception(f"--- Exception in list_custom_commands ---\n{e}")

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        try:
            if not message.author.bot:
                if (await self.cog_status("CustomCommandsCog", message.guild.id)) == True:
                    msg: str = message.content
                    prefix: str = (await get_prefix(self.bot, message))
                    if msg.startswith(prefix):
                        message_content_list = msg.replace(prefix, "").split(" ")
                        cmd = message_content_list[0]
                        t = CustomCommands()
                        t.guild_id = message.guild.id
                        t.load()
                        if cmd in t.command_name_to_message_map.keys():
                            await message.channel.send(t.command_name_to_message_map[cmd])
        except Exception as e:
            raise Exception(f"--- Exception in on_message custom_commands cog ---\n{e}")

async def setup(bot):
    await bot.add_cog(CustomCommandsCog(bot))