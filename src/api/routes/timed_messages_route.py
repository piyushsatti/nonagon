from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from timed_messages_dataclass import TimedMessages

class TimedMessagesModel(BaseModel):
    guild_id: str
    channel_id: str = None
    alias: str = None
    period: int = None
    message: str = None

@router.get('/read', status_code=status.HTTP_200_OK)
async def get_timed_messages(payload: TimedMessagesModel):
    try:
        tmp = TimedMessages()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in get_timed_messages ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_timed_messages(payload: TimedMessagesModel):
    try:
        tmp = TimedMessages()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_timed_messages ---\n{e}")

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_timed_message(payload: TimedMessagesModel):
    try:
        tmp = TimedMessages()
        tmp.guild_id = payload.guild_id
        tmp.load()
        map = tmp.alias_to_timed_message_map
        map[payload.alias] = {
            'channel_id' : payload.channel_id, 
            'period': payload.period, 
            'message': payload.message
        }
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in create_timed_message ---\n{e}")

@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_timed_message(payload: TimedMessagesModel):
    try:
        tmp = TimedMessages()
        tmp.guild_id = payload.guild_id
        tmp.load()
        removed_alias = tmp.alias_to_timed_message_map.pop(payload.alias)
        tmp.update()
        return f"Alias {removed_alias} has been removed from guild {payload.guild_id}"
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in delete_timed_message ---\n{e}")