from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from level_up_dataclass import LevelUp

class LevelUpModel(BaseModel):
    guild_id: str

@router.get("/read", status_code=status.HTTP_200_OK)
async def read_level_up(payload: LevelUpModel):
    try:
        tmp = LevelUp()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in read_level_up ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_level_up(payload: LevelUpModel):
    try:
        tmp = LevelUp()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_level_up ---\n{e}")