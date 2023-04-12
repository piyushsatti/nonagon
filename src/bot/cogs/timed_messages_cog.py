import discord
from discord.ext import commands, tasks

# Code Imports
from cog_base_class import Base

# dataclasses import
from timed_messages_dataclass import TimedMessages

class Timed(Base, name="TimedMessagesCog"):
    """Makes the bot send messages periodically"""
    def __init__(self, bot):
        super().__init__(bot)
        self.printer.start()
        self.time_interval = 0

    @commands.command()
    async def create_timed_message(self, ctx:commands.Context, channel:discord.TextChannel, alias, period, *args):
        '''Creates new timed message.'''
        if (await self.cog_status(ctx.command.cog_name, ctx.guild.id)) == True:
            try:
                message = ' '.join(args)
                t = TimedMessages()
                t.guild_id = ctx.guild.id
                t.load()
                t.alias_to_timed_message_map[alias] = [
                    str(channel.id),
                    period,
                    message
                ]
                t.update()
                await ctx.send(
                    content=f"Timed message `{message}` with alias `{alias}` now periodic every `{period}` min"
                )
            except Exception as e:
                print("--- Exception in create_timed_message ---\n", e)   

    @commands.command()
    async def delete_timed_message(self, ctx:commands.Context, alias):
        '''Deletes timed message. Format: `<#channel> <alias>`'''
        if await self.cog_status(ctx.command.cog_name, ctx.guild.id) == True:
            try:
                t = TimedMessages()
                t.guild_id = ctx.guild.id
                t.load()
                t.alias_to_timed_message_map.pop(alias)
                t.update()
                await ctx.send(
                    content=f"Deleted timed message with alias `{alias}`."
                )
            except Exception as e:
                print('--- Exception in delete_timed_message ---\n',e)
        
    @commands.command()
    async def list_timed_messages(self, ctx:commands.Context):
        '''Displays all the timed messages in the guild'''
        if (await self.cog_status(ctx.command.cog_name, ctx.guild.id)) == True:
            try:
                t = TimedMessages()
                t.guild_id = ctx.guild.id
                t.load()
                if not len(t.alias_to_timed_message_map):
                    await ctx.send(
                        content="No timed messages exists for this server."
                    )
                    return
                else:
                    embed = discord.Embed(
                        color = self.bot.color,
                        title = f"All timed messages for {ctx.guild.name}\n"
                    )
                    for key, val in t.alias_to_timed_message_map.items():
                        channel_mention = self.bot.get_channel(int(val[0])).mention
                        embed.add_field(
                            name=f'{key} => {val[2]}', 
                            value=f"Every {val[1]} minutes in {channel_mention}", 
                            inline=False\
                        )
                    await ctx.send(embed=embed)
            except Exception as e:
                print('Exception in list_timed_messages:\n',e)
    
    @tasks.loop(seconds=60.0)
    async def printer(self):
        try:
            self.time_interval += 1
            t = TimedMessages()
            for guild in self.bot.guilds:
                t.guild_id = guild.id
                t.load()
                for key, val in t.alias_to_timed_message_map.items():
                    if self.time_interval % int(val[1]) == 0:
                        channel_obj:discord.TextChannel = self.bot.get_channel(int(val[0]))
                        await channel_obj.send(val[2])
        except Exception as e:
            print(f"--- Exception in timed messages -> printer ---\n{e}")
    
    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Timed(bot))