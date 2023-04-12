import uvicorn
from distutils.log import debug
from imp import reload
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# pathing
import sys, os

sys.path.append(
    os.path.join(
        os.getcwd(),
        'src',
        'api'
    )
)

sys.path.append(
    os.path.join(
        os.getcwd(),
        'src',
        'dataclasses'
    )
)

# Routers
from routes import guild_route, custom_commands_route, timed_messages_route, reaction_roles_route, tickets_route
from routes import stat_channel_route, level_up_route, twitter_route, welcome_messages_route

app.include_router(guild_route.router, prefix="/guilds")
app.include_router(welcome_messages_route.router, prefix='/welcome-messages')
app.include_router(custom_commands_route.router, prefix="/custom-commands")
app.include_router(timed_messages_route.router, prefix="/timed-messages")
app.include_router(reaction_roles_route.router, prefix='/reaction-roles')
app.include_router(tickets_route.router, prefix='/tickets')
app.include_router(stat_channel_route.router, prefix='/stat_channel')
app.include_router(level_up_route.router, prefix='/level_up')
app.include_router(twitter_route.router, prefix='/twitter')

origins = ["*"]

# Enable Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
def shutdown_event():
    pass

@app.get("/")
async def home():
    return "Homepage."
    
if __name__ == "__main__":
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
    
    data = ["a","b"]
    
    for ele in data:
        for table in tables:
            ins = tables[f'{table}']
            ins.guild_id = ele
            ins.create()
    
    from app import app
    # uvicorn.run("peppermint_api:app", host="localhost", port=5001)
    uvicorn.run("peppermint_api:app", host="localhost", port=5001, reload=True)