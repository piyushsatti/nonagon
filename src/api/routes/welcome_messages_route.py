from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from welcome_messages_dataclass import WelcomeMessages

class WelcomeMessageModel(BaseModel):
    guild_id:str = ''
    channel_id:str = None
    background_image_url:str = None
    text_color:str = None

@router.get('/read', status_code=status.HTTP_200_OK)
async def get_welcome_messages(payload: WelcomeMessageModel):
    try:
        tmp = WelcomeMessages()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in get_welcome_messages ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_welcome_messages(payload: WelcomeMessageModel):
    try:
        tmp = WelcomeMessages()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_welcome_messages ---\n{e}")

@router.patch('/update', status_code=status.HTTP_200_OK)
async def update_welcome_messages(payload: WelcomeMessageModel):
    try:
        tmp = WelcomeMessages()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if payload.channel_id is not None:
            tmp.channel_id = payload.channel_id
        if payload.background_image_url is not None:
            tmp.background_image_url = payload.background_image_url
        if payload.text_color is not None:
            tmp.text_color = payload.text_color
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in update_welcome_messages\n{e} ---")