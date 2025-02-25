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

    def play(self):
        try:
            self._sp.start_playback()
            return "Playback started."
        except Exception as e:
            return f"Error starting playback: {e}"

    def pause(self):
        try:
            self._sp.pause_playback()
            return "Playback paused."
        except Exception as e:
            return f"Error pausing playback: {e}"

    def next_track(self):
        try:
            self._sp.next_track()
            return "Skipped to the next track."
        except Exception as e:
            return f"Error skipping track: {e}"

    def previous_track(self):
        try:
            self._sp.previous_track()
            return "Went back to the previous track."
        except Exception as e:
            return f"Error going to previous track: {e}"

    def current_track(self) -> str:
        try:
            response = self._sp.current_playback()
            if response and response.get('item'):
                return "Currently playing: " + response['item']['name']
            return "No track is currently playing."
        except Exception as e:
            return f"Error: {e}"

    def next_in_queue(self) -> str:
        try:
            response = self._sp.queue()
            if response and response.get("queue"):
                return "1st queued " + response["queue"][0]['name'] \
                    + "2nd queued " + response["queue"][1]['name'] \
                    + "3nd queued " + response["queue"][2]['name']
            return "No upcoming tracks in queue."
        except Exception as e:
            return f"Error: {e}"

    def set_volume(self, volume: int) -> str:
        try:
            # current_volume = self._sp.current_playback()[
            #   "device"]["volume_percent"]
            current_device = self._sp.current_playback()[
                "device"]["type"]
            if not current_device == "Smartphone":
                self._sp.volume(volume)
                return f"volume changed to {volume}."
            else:
                return "can not change the volume of Smartphone"
        except Exception as e:
            return f"Error chainging volume: {e}"

    def _run(
            self,
            command: Literal["play", "pause", "next",
                             "previous", "current",
                             "queued", "volume",
                             ],
            volume: Optional[int] = None
    ) -> str:
        command = command.lower().strip()
        if command in ["play"]:
            return self.play()
        elif command in ["pause"]:
            return self.pause()
        elif command in ["next"]:
            return self.next_track()
        elif command in ["previous"]:
            return self.previous_track()
        elif command in ["current"]:
            return self.current_track()
        elif command in ["queued"]:
            return self.next_in_queue()
        elif command in ["volume"]:
            if volume is None:
                return "Please provide a volume level."
            return self.set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Try 'play', 'pause',\
            'next', 'current', 'queued', 'volume' or 'previous'."
