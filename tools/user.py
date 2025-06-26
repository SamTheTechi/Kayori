import os
import random
import requests
from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from typing import Literal, Optional
load_dotenv()


class UserTool(BaseTool):
    def __init__(self, **data):
        super().__init__(**data)

    name: str = "user_controller"
    description: str = (
        "A tool for controlling the user phone by executed predefined commands. "
        "Supports commands to for find_my_phone, toggle_flashlight"
    )
    JOIN_DEVICE_ID: Optional[str] = os.getenv("JOIN_DEVICE_ID")
    JOIN_API_KEY: Optional[str] = os.getenv("JOIN_API_KEY")
    BASE_URL: str = (
                "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
                f"?apikey={JOIN_API_KEY}"
                f"&deviceId={JOIN_DEVICE_ID}"f"&text=")

    def toggle_flashlight(self):
        try:
            print("someghgin")
        except Exception as e:
            print(e)

     def find_my_phone(self):
        try:
            print("someghgin")
        except Exception as e:
            print(e)

    def _run(
            self,
            command: Literal["toggle_flashlight", "find_my_phone"],
            volume: Optional[int] = None
    ) -> str:
        command = command.lower().strip()
        if command in ["toggle_flashlight"]:
            return self._play_random()
        elif command in ["find_my_phone"]:
            return self._set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Available commands:\
            play_pause, next/skip , previous, track_info, play_random\
            , volume."
