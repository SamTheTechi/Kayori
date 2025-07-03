import os
import random
import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from langchain_core.tools import BaseTool
from typing import Literal, Optional
from pydantic import PrivateAttr
load_dotenv()


class SpotifyTool(BaseTool):
    name: str = "spotify_controller"
    description: str = (
        "A tool for controlling the user's Spotify playback."
        "Supports commands to play/pause music (start music), skip tracks, go to the previous track, "
        "get currently playing track information, adjust volume, toggle shuffle and play_random"
        "prefer using play_random when ever use ask for music insted of play_pause."
    )
    _sp: spotipy.Spotify = PrivateAttr()
    JOIN_DEVICE_ID: Optional[str] = os.getenv("JOIN_DEVICE_ID")
    JOIN_API_KEY: Optional[str] = os.getenv("JOIN_API_KEY")

    def __init__(self, **data):
        super().__init__(**data)
        self._sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT"),
            scope="user-modify-playback-state user-read-playback-state \
            user-read-recently-played user-read-currently-playing\
            user-library-read playlist-read-private"
        ))

    # Toggles playback (play/pause) on Spotify.
    def _play_pause(self):
        try:
            # If there's at least one active device, get current playback state
            devices = self._sp.devices()
            active_devices = devices.get("devices", [])
            if len(active_devices) < 1:
                # Only send Join push if API key and device ID are present
                if self.JOIN_API_KEY and self.JOIN_DEVICE_ID:
                    url = (
                        "https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush"
                        f"?apikey={self.JOIN_API_KEY}"
                        f"&deviceId={self.JOIN_DEVICE_ID}"
                        "&text=spotify_command"
                    )
                    response = requests.get(url)
                    if response.status_code == 200:
                        return "Spotify opend and start playing on androind phone"
                    else:
                        return f"Failed to trigger Join push. Status: {response.status_code}"
            else:
                current_status = self._sp.current_playback()

                if current_status and current_status.get("is_playing"):
                    self._sp.pause_playback()
                    return "Playback paused"
                else:
                    self._sp.start_playback()
                    return "Playback resumed."

            return "No active devices present"
        except Exception as e:
            return f"Error making playback request: {e}"

    # Skips to the next track in the Spotify queue.
    def _next_track(self):
        try:
            response = self._sp.queue()
            self._sp.next_track()
            next_song = response["queue"][0]["name"] if response.get(
                "currently_playing") is not None else None
            return f"Skipped to the next track {next_song}."
        except Exception as e:
            return f"Error skipping track: {e}"

    # Goes back to the previous track on Spotify.
    def _previous_track(self):
        try:
            self._sp.previous_track()
            return "Went back to the previous track."
        except Exception as e:
            return f"Error going to previous track: {e}"

    # Retrieves information about the currently playing track.
    def _track_info(self) -> str:
        try:
            response = self._sp.queue()
            if response.get("currently_playing") is not None:
                return f"currently playing:{response["currently_playing"]
                                            ["name"]},next in queue:{response["queue"][0]["name"]}"
            else:
                return "No track is currently playing."
        except Exception as e:
            return f"Error: {e}"

    # Sets the playback volume on Spotify.
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

    # Plays a random track from recently played or queue.
    def _play_random(self) -> str:
        try:
            # 21, don't ask me why 21
            tracks_object = self._sp.current_user_top_tracks(limit=21, time_range="short_term")
            tracks = tracks_object['items']
            tracks_to_play = random.sample(tracks, 3)
            uris = [track["uri"] for track in tracks_to_play]

            for uri in uris:
                self._sp.add_to_queue(uri=uri)

            self._sp.next_track()

            return f"Playing: {tracks_to_play[0]['name']}"
        except Exception as e:
            return f"Error playing a song: {e}"

    # Executes a Spotify command.
    def _run(
        self,
        command: Literal["play&pause", "next", "skip" "previous", "track_info", "volume", "play_random"],
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
        elif command in ["play_random"]:
            return self._play_random()
        elif command in ["volume"]:
            if volume is None:
                return "Please provide a volume level."
            return self._set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Available commands:\
            play_pause, next/skip , previous, track_info, play_random\
            , volume."
