from json import loads
from requests import request

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from ticket_dataclass import TicketDataclass

class TicketsModel(BaseModel):
    guild_id: str
    title: str = None
    description: str = None
    message_id: str = None
    channel_id: str = None
    category_id: str = None
    ticket_emoji: str = "%F0%9F%93%A7&%F0%9F%94%A5"

@router.get("/read", status_code=status.HTTP_200_OK)
async def read_tickets(payload: TicketsModel):
    try:
        tmp = TicketDataclass()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in read_tickets ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_tickets(payload: TicketsModel):
    try:
        tmp = TicketDataclass()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_tickets ---\n{e}")

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketsModel):
    try:
        tmp = TicketDataclass()
        tmp.guild_id = payload.guild_id
        tmp.load()
        resp = request(
            method="POST", 
            url=f"https://discord.com/api/v10/channels/{payload.channel_id}/messages",
            headers={"Authorization": "Bot "},
            json={
                "content": "Hello, World!",
                "embeds": [{
                    "title": payload.title,
                    "description": payload.description
                    }]
                }
        )
        ticket_message_id = (loads(resp.content))["id"]
        resp = request(
            method="PUT", 
            url=f"https://discord.com/api/v10/channels/{payload.channel_id}/messages/{ticket_message_id}/reactions/{payload.ticket_emoji}/@me",
            headers={"Authorization": "Bot "}
        )
        tmp.message_to_ticket_map[ticket_message_id]={
            "title":payload.title,
            "description":payload.description,
            "channel_id":payload.channel_id,
            "category_id":payload.category_id,
            "ticket_channels":[]
        }
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in create_ticket ---\n{e}")

@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_ticket(payload: TicketsModel):
    try:
        tmp = TicketDataclass()
        tmp.guild_id = payload.guild_id
        tmp.load()
        tmp.message_to_ticket_map.pop(payload.message_id)
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in delete_ticket ---\n{e}")