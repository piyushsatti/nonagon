import discord
from discord.ext import commands, tasks

# Code Imports
from cog_base_class import Base

# dataclasses
from stat_channel_dataclass import StatChannel

class Stats(Base, name="StatsChannelCog"):
    """Creates a channel to show server information"""
    def __init__(self, bot):
        super().__init__(bot)
        self.stat_fetch.start()

    @commands.command()
    async def set_stats(self, ctx:commands.Context):
        category = await ctx.guild.create_category("Server Info")
        channel = await category.create_voice_channel(f"Members: {len(ctx.guild.members)}")
        try:
            t = StatChannel()
            t.guild_id = ctx.guild.id
            t.load()
            t.stat_channel_id = channel.id
            t.update()
            await ctx.send("Created a stat channel for this server! The counter will be updated every 10 minutes!")
            ov = discord.PermissionOverwrite()
            ov.connect = False
            await channel.set_permissions(
                    overwrite=ov,
                    target=ctx.guild.default_role
                )
        except Exception as e:
            print(e)

    @tasks.loop(minutes=10)
    async def stat_fetch(self):
        try:
            t = StatChannel()
            for guild in self.bot.guilds:
                t.guild_id = guild.id
                t.load()
                if (await self.cog_status("StatsChannelCog", guild.id)) == True and t.stat_channel_id is not None:
                    vc = self.bot.get_channel(int(t.stat_channel_id))
                    await vc.edit(name=f'Members: {len(vc.guild.members)}')
        except Exception as e:
            print(f"--- Exception in stat_fetch ---\n {e}")

    @stat_fetch.before_loop
    async def before_stat_fetch(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Stats(bot))