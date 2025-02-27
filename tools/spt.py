import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from langchain_core.tools import BaseTool
from typing import Literal, Optional
from pydantic import PrivateAttr
load_dotenv()


class SpotifyTool(BaseTool):
    name: str = "spotify_controller"
    description: str = "Control user's spotify"
    _sp: spotipy.Spotify = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT"),
            scope="user-modify-playback-state,user-read-playback-state"
        ))

    def _play_pause(self):
        try:
            current_status = self._sp.current_playback()
            if current_status["is_playing"]:
                self._sp.pause_playback()
                return "Playback paused"
            else:
                self._sp.start_playback()
                return "Playback resumed."
        except Exception as e:
            return f"Error making playback request: {e}"

    def _next_track(self):
        try:
            self._sp.next_track()
            return "Skipped to the next track."
        except Exception as e:
            return f"Error skipping track: {e}"

    def _previous_track(self):
        try:
            self._sp.previous_track()
            return "Went back to the previous track."
        except Exception as e:
            return f"Error going to previous track: {e}"

    def _track_info(self) -> str:
        try:
            response = self._sp.queue()
            if response.get("currently_playing") is not None:
                return f"currently playing:{response["currently_playing"]["name"]},next in queue:{response["queue"][0]["name"]}"
            else:
                return "No track is currently playing."
        except Exception as e:
            return f"Error: {e}"

    def _set_volume(self, volume: int) -> str:
        try:
            playback = self._sp.current_playback()
            device_type = playback.get("device", {}).get("type")
            if device_type and device_type.lower() == "smartphone":
                return "Cannot change volume on a smartphone."

            self._sp.volume(volume)
            return f"Volume set to {volume}."
        except Exception as e:
            return f"Error chainging volume: {e}"

    def _run(
            self,
            command: Literal["play&pause", "next",
                             "previous", "track_info", "volume",
                             ],
            volume: Optional[int] = None
    ) -> str:
        command = command.lower().strip()
        if command in ["play&pause"]:
            return self._play_pause()
        elif command in ["next"]:
            return self._next_track()
        elif command in ["previous"]:
            return self._previous_track()
        elif command in ["track_info"]:
            return self._track_info()
        elif command in ["volume"]:
            if volume is None:
                return "Please provide a volume level."
            return self._set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Available commands:\
            play_pause, next, previous, track_info, volume."
