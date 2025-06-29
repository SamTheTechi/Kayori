import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from typing import Literal, Optional
load_dotenv()


# A tool for controlling the user's phone with predefined commands.
class UserTool(BaseTool):
    def __init__(self, **data):
        super().__init__(**data)

    name: str = "user_controller"
    description: str = (
        "A tool for controlling the user phone by executed predefined commands."
        "Supports commands to for find_my_phone, toggle_flashlight, speak_to_user"
        "use this functions at your will speak_to_user"
    )
    JOIN_DEVICE_ID: Optional[str] = os.getenv("JOIN_DEVICE_ID")
    JOIN_API_KEY: Optional[str] = os.getenv("JOIN_API_KEY")
    BASE_URL: str = (
        "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
        f"?apikey={JOIN_API_KEY}"
        f"&deviceId={JOIN_DEVICE_ID}"f"&text=")

    # Toggles the device's flashlight.
    def _toggle_flashlight(self):
        try:
            response = requests.get(f"{self.BASE_URL}flash_command")
            if response.status_code == 200:
                return "flash light toggled"
            else:
                return "Can't toggle users flash light"

        except Exception as e:
            print(e)

    # Triggers the device to play a sound to help locate it.
    def _find_my_phone(self):
        try:
            response = requests.get(f"{self.BASE_URL}fmp_command")
            if response.status_code == 200:
                return "ringed your phone"
            else:
                return "Can't locate users phone"

        except Exception as e:
            print(e)

    def _speak_to_user(self, content: str):
        try:
            response = requests.get(f"{self.BASE_URL}say={content}")

            if response.status_code == 200:
                return "said what i wanted to say!"
            else:
                print("sucks")
                return "seems like some issue, fallback to sending test"

        except Exception as e:
            print(e)

    def _run(self, command: Literal["toggle_flashlight", "find_phone", "speak_to_user"], content: Optional[str] = None) -> str:
        command = command.lower().strip()

        if command in ["toggle_flashlight"]:
            return self._toggle_flashlight()
        elif command in ["find_phone"]:
            return self._find_my_phone()
        elif command in ["speak_to_user"]:
            if content is None:
                return "you need to provide content to speak to user"
            return self._speak_to_user(str(content))
        else:
            return f"Command '{command}' not recognized. Available commands: toggle_flashlight, find_phone, speak_to_user."
