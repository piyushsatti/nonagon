import discord
import re
import wavelink
from discord.ext import commands, menus
from typing import Union
import random
from datetime import timedelta

# Code Imports
from cog_base_class import Base

RURL = re.compile('https?:\/\/(?:www\.)?.+')
playlist_regex = r'(https://)(www\.)?(youtube\.com)\/(?:watch\?v=|playlist)?(?:.*)?&?(list=.*)'

class Music(Base, name="MusicCog"):
    """Enables you to play music in a voice channel"""
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='localhost',
                                            port=2333,
                                            password='youshallnotpass',
                                            region='india')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        if not ctx.voice_client:
            embed = discord.Embed(
            color = self.bot.color,
            title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client   
        vc: player = ctx.voice_client
        if vc.loop:
            return await vc.play(track)
        next_song = vc.queue.get()
        await vc.play(next_song)
        embed = discord.Embed(
            color = self.bot.color,
            title = f"Now playing: {vc.queue[0]}"
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        '''Disconnects from the voice channel'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        vc: wavelink.Player = ctx.voice_client
        await vc.stop()
        vc.queue.reset()
        await vc.disconnect()
        embed = discord.Embed(
            color = self.bot.color,
            title = "Disconnected the player."
        )
        await ctx.send(embed=embed)
    @commands.command()
    async def playstream(self, ctx: commands.Context, url: str):
        """Plays a livestream from given URL"""
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        track = await vc.node.get_tracks(query=url, cls=wavelink.LocalTrack)
        if vc.queue.is_empty and not vc.is_playing():

            embed = discord.Embed(
                color = self.bot.color,
                title = f"Playing {track.title}"
            )
        await ctx.send(embed=embed)
        await vc.play(track[0])
        
    @commands.command()
    async def play(self, ctx, *, song: wavelink.YouTubeTrack):
        """Plays a song."""
        if ctx.author.voice is None:
            return await ctx.send("You are not in a voice channel")
        vc: wavelink.Player = ctx.voice_client or await ctx.author.voice.channel.connect(cls=wavelink.Player)
        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(song)
            em = discord.Embed(color=self.bot.color)
            em.add_field(name="▶ Playing",
                         value=f"[{song.title}]({song.uri})", inline=False)
            em.add_field(name="⌛ Song Duration", value=str(
                timedelta(seconds=song.duration)), inline=False)
            em.add_field(name="👥 Requested by",
                         value=ctx.author.mention, inline=False)
            em.add_field(name="🎵 Song by", value=song.author, inline=False)
            em.set_thumbnail(url=vc.source.thumbnail)
            await ctx.send(embed=em)
        else:
            await vc.queue.put_wait(song)
            await ctx.send(f"Added `{song.title}` to the queue...")
        vc.ctx = ctx
        setattr(vc, "loop", False)

    @commands.command(aliases=['pa', 'wait'])
    async def pause(self, ctx):
        '''Pauses the song'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            embed = discord.Embed(
                color = self.bot.color,
                title = 'I am not currently playing anything!'
            )
            return await ctx.send(embed=embed)
        embed = discord.Embed(
            color = self.bot.color,
            title = 'Pausing the song!'
        )
        await ctx.send(embed=embed)
        await vc.set_pause(True)
    
    @commands.command()
    async def resume(self, ctx):
        '''Resumes the song'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing:
            embed = discord.Embed(
                    color = self.bot.color,
                    title = 'I am not currently playing anything!'
                )
            return await ctx.send(embed=embed)
        embed = discord.Embed(
                color = self.bot.color,
                title = 'Resuming the song!'
            )
        await ctx.send(embed=embed)
        await vc.set_pause(False)

    @commands.command(aliases=['v', 'vol'])
    async def volume(self, ctx, *, vol: int):
        '''Sets the volume'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client

        vol = max(min(vol, 1000), 0)
        embed = discord.Embed(
                color = self.bot.color,
                title = f'Setting the player volume to `{vol}`!'
            )
        await ctx.send(embed=embed)
        await vc.set_volume(vol)

    @commands.command()
    async def loop(self, ctx: commands.Context):
        '''Loops the song'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        try:
            vc.loop = True
        except Exception:
            setattr(vc, "loop", False)
        if vc.loop:
            embed = discord.Embed(
                color = self.bot.color,
                title = "Looping! 🔁"
            )
            return await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                color = self.bot.color,
                title = "Loop is disabled."
            )
            return await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx: commands.Context):
        '''Displays the current queue'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.queue.is_empty:
            embed = discord.Embed(
                color = self.bot.color,
                title = "Queue is empty."
            )
            return await ctx.send(embed=embed)
        em = discord.Embed(title="Queue", description=f"Now Playing: `{vc.track.title}`", color = self.bot.color)
        queue = vc.queue.copy()
        song_count = 1
        for song in queue:
            em.add_field(name=f"Song Num {song_count}", value = f"`{song.title}`")
            song_count += 1
        return await ctx.send(embed=em)

    @commands.command()
    async def nowplaying(self, ctx: commands.Context):
        '''Displays the song currently playing'''
        if not ctx.voice_client:
            embed = discord.Embed(
                color = self.bot.color,
                title = "I'm not in a channel."
            )
            await ctx.send(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                color = self.bot.color,
                title = "Please join a voice channel."
            )
            return await ctx.send(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.is_playing():
            return await ctx.send("Nothing is playing")
        em = discord.Embed(title = f"Now playing {vc.track.title}", description=f"Artist: {vc.track.author}", color=self.bot.color)
        return await ctx.send(embed=em)

    @commands.command()
    async def skip(self, ctx, seek=None):
        '''Skips the song'''
        vc: wavelink.Player = ctx.voice_client
        if not seek:
            if not vc.queue.is_empty:
                await vc.stop()

async def setup(bot):
    await bot.add_cog(Music(bot))