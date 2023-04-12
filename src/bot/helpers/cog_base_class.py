import discord
from discord.ext import commands
from pydantic import BaseModel

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

class BaseCog(BaseModel):
    guild_id: str
    toggle: int

    def read():
        pass

class Base(commands.Cog, name="BaseCog"):
    
    def __init__(self, bot):
        self.bot = bot

    async def cog_status(self, cog_name, guild_id):
        try:
            match cog_name:
                case 'CustomCommandsCog':
                    a: BaseCog = CustomCommands()
                case 'LevelUpCog':
                    a: BaseCog = LevelUp()
                case 'ReactionRolesCog':
                    a: BaseCog = ReactionRole()
                case 'StatsChannelCog':
                    a: BaseCog = StatChannel()
                case 'TimedMessagesCog':
                    a: BaseCog = TimedMessages()
                case default:
                    a: BaseCog = None
            assert a != None, f"--- Exception in cog_status ---\nThe cog name does not match any dataclass"
            a.guild_id = guild_id
            res = a.read()
            if res[1] == 1:
                return True
            else:
                return False
        except Exception as e:
            raise Exception(f"--- Exception in cog_status ---\n{e}")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'