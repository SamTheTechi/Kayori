import os
import aiohttp
from services.state_store import get_live_location
from util.geo_utli import aget_current_location
from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from typing import Literal, Optional, Type
from pydantic import BaseModel
load_dotenv()


class UserToolArgs(BaseModel):
    command: Literal["toggle_flashlight", "find_phone", "speak_to_user", "user_location"]
    content: Optional[str] = None


# A tool for controlling the user's phone with predefined commands.
class UserTool(BaseTool):
    def __init__(self, **data):
        super().__init__(**data)

    name: str = "user_controller"
    description: str = (
        "A tool for controlling the user phone by executed predefined commands."
        "Supports commands to for find_my_phone, toggle_flashlight, speak_to_user"
        "speak_to_user can be used freely to express thoughts, emotions, or reactions when ever you wants"
    )
    JOIN_DEVICE_ID: Optional[str] = os.getenv("JOIN_DEVICE_ID")
    JOIN_API_KEY: Optional[str] = os.getenv("JOIN_API_KEY")
    BASE_URL: str = (
        "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
        f"?apikey={JOIN_API_KEY}"
        f"&deviceId={JOIN_DEVICE_ID}"f"&text=")
    args_schema: Type[BaseModel] = UserToolArgs

    # Toggles the device's flashlight.

    async def _toggle_flashlight(self):
        try:
            async with aiohttp.ClientSession() as client:
                response = await client.get(f"{self.BASE_URL}flash_command")
                if response.status == 200:
                    return "flash light toggled"
                else:
                    return "Can't toggle users flash light"

        except Exception as e:
            print(e)

    # Triggers the device to play a sound to help locate it.
    async def _find_my_phone(self):
        try:
            async with aiohttp.ClientSession() as client:
                response = await client.get(f"{self.BASE_URL}fmp_command")
                if response.status == 200:
                    return "ringed your phone"
                else:
                    return "Can't locate users phone"

        except Exception as e:
            print(e)

    async def _speak_to_user(self, content: str):
        try:
            async with aiohttp.ClientSession() as client:
                response = await client.get(f"{self.BASE_URL}say={content}")
                if response.status == 200:
                    return "said what i wanted to say!"
                else:
                    print("sucks")
                    return "seems like some issue, fallback to sending test"

        except Exception as e:
            print(e)

    async def _user_location(self):
        try:
            coordinates = await get_live_location()
            respone = await aget_current_location(coordinates["latitude"], coordinates["longitude"])

            suburb = respone["suburb"]
            city = respone["city"]
            state = respone["state"]

            return f"User seems to be in {suburb} {city} {state}"
        except Exception as e:
            print(e)
            return "seems like i can't locate users locations"

    async def _arun(
        self,
        command: Literal["toggle_flashlight", "find_phone", "speak_to_user", "user_location"],
        content: Optional[str] = None
    ) -> str:
        command = command.lower().strip()

        if command in ["toggle_flashlight"]:
            return await self._toggle_flashlight()
        elif command in ["find_phone"]:
            return await self._find_my_phone()
        elif command in ["user_location"]:
            return await self._user_location()
        elif command in ["speak_to_user"]:
            if content is None:
                return "you need to provide content to speak to user"
            return await self._speak_to_user(str(content))
        else:
            return f"Command '{command}' not recognized. Available commands: toggle_flashlight, find_phone, user_location, speak_to_user."

    def _run(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use async version of this tool.")
