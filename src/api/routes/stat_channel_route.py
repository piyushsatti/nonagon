from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from stat_channel_dataclass import StatChannel

class StatChannelModel(BaseModel):
    guild_id: str

@router.get("/read", status_code=status.HTTP_200_OK)
async def read_stat_channel(payload: StatChannelModel):
    try:
        tmp = StatChannel()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in read_tickets ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_stat_channel(payload: StatChannelModel):
    try:
        tmp = StatChannel()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_stat_channel ---\n{e}")