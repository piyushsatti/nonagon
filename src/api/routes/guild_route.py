from requests import request

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from guild_data_dataclass import GuildData

class GuildDataModel(BaseModel):
    guild_id: str
    guild_prefix: str = None

@router.get('/', status_code=status.HTTP_200_OK)
async def get_bot_guilds():
    try:
        return request(
                method="GET", 
                url=f"http://discordapp.com/api/users/@me/guilds",
                headers={"Authorization": "Bot "}
            ).json()

    except Exception as e:
        HTTPException(status_code=404, detail=f"--- Exception in get_bot_guilds ---\n{e}")

@router.get('/read', status_code=status.HTTP_200_OK)
async def get_guild_data(payload: GuildDataModel):
    try:
        tmp = GuildData()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in get_guild_data ---\n{e}")

@router.get('/state', status_code=status.HTTP_200_OK)
async def get_guild_channels(payload: GuildDataModel):
    try:
        guild_channels = request(
            method="GET", 
            url=f"https://discord.com/api/v10/guilds/{payload.guild_id}/channels",
            headers={"Authorization": "Bot "},
            json={
                "content": payload.message_content,
                "embeds": payload.embed
                }
        ).json()

        guild_roles = request(
            method="GET", 
            url=f"https://discord.com/api/v10/guilds/{payload.guild_id}/roles",
            headers={"Authorization": "Bot "},
            json={
                "content": payload.message_content,
                "embeds": payload.embed
                }
        ).json()

        return {
            'channels': guild_channels,
            'roles': guild_roles
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in get_guild_roles ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_guild(payload: GuildDataModel):
    try:
        tmp = GuildData()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_guild ---\n{e}")

@router.patch('/update', status_code=status.HTTP_200_OK)
async def update_guild(payload: GuildDataModel):
    try:
        tmp = GuildData()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if payload.guild_prefix is not None:
            tmp.guild_prefix
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in update_guild ---\n{e}")