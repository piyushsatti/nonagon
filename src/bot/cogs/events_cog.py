import discord
from discord.ext import commands
from requests import PreparedRequest

# Code Imports
from cog_base_class import Base
from peppermint_bot import add_guilds_to_db, check_guilds, get_prefix

# Dataclasses Imports
from welcome_messages_dataclass import WelcomeMessages
from custom_commands_dataclass import CustomCommands

class EventsCog(Base, name="EventsCog"):

    def __init__(self, bot):
        super().__init__(bot)
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await add_guilds_to_db([guild.id])

    @commands.Cog.listener()
    async def on_ready(self):
        await check_guilds(self.bot)
        print(f'Ready!\n Logged in as ----> {self.bot.user}\n ID:{self.bot.user.id}')

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        embed = discord.Embed(colour=discord.Colour.green())
        a = WelcomeMessages()
        a.guild_id = member.guild.id
        a.load()
        req = PreparedRequest()
        req.prepare_url(
            url='https://api.xzusfin.repl.co/card?',
            params={
                'avatar': str(member.display_avatar.url),
                'middle': 'welcome',
                'name': str(member.name),
                'bottom': str('on ' + member.guild.name),
                'text': a.text_color,
                'avatarborder': '#CCCCCC',
                'avatarbackground': '#CCCCCC',
                'background': a.background_image_url
            }
        )
        embed.set_image(url=req.url)
        # creating channel object
        channel = self.bot.get_channel(int(a.channel_id))
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error:discord.errors):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please pass in all requirements.')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You dont have all the requirements or permissions for using this command :angry:")
        if isinstance(error, commands.CommandNotFound):
            prefix: str = (await get_prefix(self.bot, ctx.message))
            if ctx.message.content.startswith(prefix):
                cmd = ctx.message.content.replace(prefix, "")
                a = CustomCommands()
                a.guild_id = ctx.guild.id
                a.load()
                if cmd not in a.command_name_to_message_map.keys():
                    await ctx.send("Invalid command. Try `help` to figure out commands")

async def setup(bot):
    await bot.add_cog(EventsCog(bot))