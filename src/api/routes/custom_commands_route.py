from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
router = APIRouter()

from custom_commands_dataclass import CustomCommands

class CustomCommandsModel(BaseModel):
    guild_id: str
    command_name: str
    message: str = None

@router.get('/read', status_code=status.HTTP_200_OK)
async def get_custom_commands(payload: CustomCommandsModel):
    try:
        tmp = CustomCommands()
        tmp.guild_id = payload.guild_id
        return tmp.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in get_custom_commands ---\n{e}")

@router.patch('/toggle', status_code=status.HTTP_200_OK)
async def toggle_custom_commands(payload: CustomCommandsModel):
    try:
        tmp = CustomCommands()
        tmp.guild_id = payload.guild_id
        tmp.load()
        if tmp.toggle == 0:
            tmp.toggle = 1
        else:
            tmp.toggle = 0
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in toggle_custom_commands ---\n{e}")

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_custom_commands(payload: CustomCommandsModel):
    try:
        tmp = CustomCommands()
        tmp.guild_id = payload.guild_id
        tmp.load()
        map = tmp.command_name_to_message_map
        map[payload.command_name] = payload.message
        tmp.update()
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in create_custom_commands ---\n{e}")

@router.delete('/delete', status_code=status.HTTP_200_OK)
async def delete_custom_command(payload: CustomCommandsModel):
    try:
        tmp = CustomCommands()
        tmp.guild_id = payload.guild_id
        tmp.load()
        removed_command = tmp.command_name_to_message_map.pop(payload.command_name)
        tmp.update()
        return f"Command {removed_command} has been removed from guild {payload.guild_id}"
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"--- Exception in delete_custom_command ---\n{e}")