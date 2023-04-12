from json import loads
from random import randint
from requests import request
from time import sleep
from urllib.parse import quote_plus

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from reaction_roles_dataclass import ReactionRole

class ReactionRolesModel(BaseModel):
    guild_id: str
    channel_id: str = None
    message_id: str = None
    message_content: str = None
    embed: list = [] # [{"title":"smth","description":"smth"}]
    reaction_to_role_map: dict = {} # {id:emoji}

@router.get("/read", status_code=status.HTTP_200_OK)
async def read_reaction_roles(payload: ReactionRolesModel):
    try:
        tmp = ReactionRole()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in read_reaction_roles ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_reaction_roles(payload: ReactionRolesModel):
    try:
        tmp = ReactionRole()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_reaction_roles ---\n{e}")

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_reaction_role(payload: ReactionRolesModel):
    try:
        tmp = ReactionRole()
        tmp.guild_id = payload.guild_id
        tmp.load()

        resp = request(
            method="POST", 
            url=f"https://discord.com/api/v10/channels/{payload.channel_id}/messages",
            headers={"Authorization": "Bot "},
            json={
                "content": payload.message_content,
                "embeds": payload.embed
                }
        )

        message_id = (loads(resp.content))["id"]
        
        for ele in payload.reaction_to_role_map.values():
            resp = request(
                method="PUT", 
                url=f"https://discord.com/api/v10/channels/{payload.channel_id}/messages/{message_id}/reactions/{quote_plus(ele)}/@me",
                headers={"Authorization": "Bot "}
            )
            sleep(1+randint(1,3))

        tmp.message_role_reaction_map[message_id]={
            "channel_id": payload.channel_id, 
            "message_content": payload.message_content, 
            "embed": payload.embed, 
            "map": payload.reaction_to_role_map
        }
        tmp.update()

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in create_reaction_role ---\n{e}")

@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_reaction_role(payload: ReactionRolesModel):
    try:
        tmp = ReactionRole()
        tmp.guild_id = payload.guild_id
        tmp.load()
        tmp.message_role_reaction_map.pop(payload.message_id)
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in delete_reaction_role ---\n{e}")