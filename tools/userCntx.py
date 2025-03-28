import os
from util.store import get_last_time, location
from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from typing import Literal, Optiona
from pydantic import PrivateAttr
load_dotenv()


class UserContext(BaseTool):
    name: str = "UserContext"
    description: str = (
        "This tool provides user-specific contextual information, including their location, "
        "current weather conditions It helps personalize responses "
    )

    def _get_user_location():

    def _run(
            self,
            command: Literal["play&pause", "next", "skip"
                             "previous", "track_info",
                             "volume", "toggle_suffle",
                             "surprise_me"
                             ],
            volume: Optional[int] = None
    ) -> str:
        command = command.lower().strip()
        if command in ["play&pause"]:
            return self._play_pause()
        elif command in ["next", "skip"]:
            return self._next_track()
        elif command in ["previous"]:
            return self._previous_track()
        elif command in ["track_info"]:
            return self._track_info()
        elif command in ["toggle_suffle"]:
            return self._toggle_shuffle()
        elif command in ["surprise_me"]:
            return self._surprise_me()
        elif command in ["volume"]:
            if volume is None:
                return "Please provide a volume level."
            return self._set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Available commands:\
            play_pause, next/skip , previous, track_info, toggle_suffle ,surprise_me\
            , volume."
