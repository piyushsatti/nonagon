import discord, os, DiscordUtils
from discord.ext import commands
from pretty_help import PrettyHelp

# pathing
import sys, os

sys.path.append(
    os.path.join(
        os.getcwd(),
        'src',
        'bot'
    )
)

sys.path.append(
    os.path.join(
        os.getcwd(),
        'src',
        'dataclasses'
    )
)

# Dataclasses Imports
from guild_data_dataclass import GuildData
from level_up_dataclass import LevelUp
from reaction_roles_dataclass import ReactionRole
from stat_channel_dataclass import StatChannel
from ticket_dataclass import TicketDataclass
from twitter_dataclass import TwitterDataclass
from welcome_messages_dataclass import WelcomeMessages
from custom_commands_dataclass import CustomCommands
from timed_messages_dataclass import TimedMessages

############ Helpers ###########

async def get_prefix(bot, message: discord.Message):
    try:
        ins = GuildData()
        guild_id = message.guild.id
        assert type(guild_id) == int, "Guild Id not an integer"
        ins.guild_id = str(guild_id)
        ins.load()
        return ins.guild_prefix
    except Exception as e:
        raise Exception(f"--- Exception in get_prefix ---\n{e}")

async def create_tables():
    tables = {
        'GuildData': GuildData(),
        'LevelUp': LevelUp(),
        'ReactionRole': ReactionRole(),
        'StatChannel': StatChannel(),
        'TicketDataclass': TicketDataclass(),
        'TwitterDataclass': TwitterDataclass(),
        'WelcomeMessages': WelcomeMessages(),
        'CustomCommands': CustomCommands(),
        'TimedMessages': TimedMessages()
    }
    
    for k in tables.keys():
        tables[k].create_table(
            tables[k].table_name,
            tables[k].meta_data
        )

async def add_guilds_to_db(data):
    tables = {
        'GuildData': GuildData(),
        'LevelUp': LevelUp(),
        'ReactionRole': ReactionRole(),
        'StatChannel': StatChannel(),
        'TicketDataclass': TicketDataclass(),
        'TwitterDataclass': TwitterDataclass(),
        'WelcomeMessages': WelcomeMessages(),
        'CustomCommands': CustomCommands(),
        'TimedMessages': TimedMessages()
    }
    
    for ele in data:
        for table in tables:
            ins = tables[f'{table}']
            ins.guild_id = ele
            ins.create()

async def check_guilds(bot):
    a = [guild.id for guild in bot.guilds]
    add_guilds_to_db(a)

def progress_bar(index, total, bar_len=50, title='Please wait'):
    '''
    index is expected to be 0 based index. 
    0 <= index < total
    '''
    percent_done = (index+1)/total*100
    percent_done = round(percent_done, 1)

    done = round(percent_done/(100/bar_len))
    togo = bar_len-done

    done_str = '█'*int(done)
    togo_str = '░'*int(togo)

    print(f'\t⏳ {title}: [{done_str}{togo_str}] {percent_done}% done         ')#, end='\r')

    if round(percent_done) == 100:
        print('\t✅ ')

async def load_extensions():
    try:
        path_to_cogs = os.path.join(
            os.getcwd(), 
            'src', 
            'bot', 
            'cogs'
        )
        total_len = len(
            os.listdir(path_to_cogs)
        )
        for i, fn in enumerate(os.listdir(path_to_cogs)):
            if fn.endswith(".py") and '__init__' not in fn:
                    await bot.load_extension(f"cogs.{fn[:-3]}")
                    title = f"Loaded cog {fn}."
            progress_bar(i, total_len, 50, title)
    except Exception as e:
        title = f"Error in cog {fn[:-3]}"
        progress_bar(i, total_len, 50, title)
        raise Exception(f"--- Exception in loading extension {fn} ---\n{e}")

async def peppermint():
    async with bot:
        bot.tracker = DiscordUtils.InviteTracker(bot)
        await bot.start('')

###################### ------- ########################

owners = []
bot = commands.Bot(
    command_prefix=get_prefix, 
    intents=discord.Intents().all(), 
    owner_ids=set(owners), 
    help_command=PrettyHelp(
        color=0xe86f52, 
        sort_commands=True, 
        show_index=True, 
        no_category=None 
    )
)

bot.multiplier = 1
bot.color = 0xe86f52

@commands.is_owner()
@bot.command(hidden=True) 
async def load(ctx, extension):
    await bot.load_extension(f"{extension}")
    await ctx.send(f"Loaded {extension}!")

@commands.is_owner()
@bot.command(hidden=True)
async def reload(ctx, extension):
    await bot.reload_extension(f"{extension}")
    await ctx.send(f"Reloaded {extension}!")

@commands.is_owner()
@bot.command(hidden=True)
async def unload(ctx, extension):
    await bot.unload_extension(f"{extension}")
    await ctx.send(f"Unloaded {extension}!")

@bot.event
async def on_ready():
    await create_tables()
    await load_extensions()
    a = [guild.id for guild in bot.guilds]
    await add_guilds_to_db(a)

if __name__ == '__main__':
    import asyncio
    asyncio.run(peppermint())