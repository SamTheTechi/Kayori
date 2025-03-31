import random
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
    description: str = (
        "A tool for controlling the user's Spotify playback. "
        "Supports commands to play/pause music, skip tracks, go to the previous track, "
        "get currently playing track information, adjust volume, toggle shuffle, and "
        "queue a random track from recent plays or the queue."
    )
    _sp: spotipy.Spotify = PrivateAttr()

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
            response = self._sp.queue()
            self._sp.next_track()
            next_song = response["queue"][0]["name"] if response.get(
                "currently_playing") is not None else None
            print(next_song)
            return f"Skipped to the next track {next_song}."
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
                return f"currently playing:{response["currently_playing"]
                                            ["name"]},next in queue:{response["queue"][0]["name"]}"
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

    def _toggle_shuffle(self) -> str:
        try:
            playback = self._sp.current_playback()
            if not playback or "shuffle_state" not in playback:
                return "Unable to retrieve shuffle state. Make sure playback is active."
            new = not playback["shuffle_state"]
            self._sp.shuffle(new)
            return "Shuffle turned on." if new else "Shuffle turned off."
        except Exception as e:
            return f"Error toggling shuffle: {e}"

    def _play_random(self) -> str:
        try:
            queue = self._sp.queue().get("queue", [])
            if not queue or len(queue) < 5:
                last_played = self._sp.current_user_recently_played(limit=10)
                track = random.choice(last_played)
                uri = track["uri"]
            else:
                queue_subset = queue[5:min(len(queue), 10)]
                track = random.choice(queue_subset)
                uri = track["uri"]

            self._sp.add_to_queue(uri=uri)
            self._sp.next_track()

            return f"Surprise! Playing: {track['name']} by {', '.join(artist['name'] for artist in track['artists'])} 🎵"

        except Exception as e:
            return f"Error playing a surprise song: {e}"

    def _run(
            self,
            command: Literal["play&pause", "next", "skip"
                             "previous", "track_info",
                             "volume", "toggle_suffle",
                             "play_random"
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
        elif command in ["play_random"]:
            return self._play_random()
        elif command in ["volume"]:
            if volume is None:
                return "Please provide a volume level."
            return self._set_volume(int(volume))
        else:
            return f"Command '{command}' not recognized. Available commands:\
            play_pause, next/skip , previous, track_info, toggle_suffle , play_random\
            , volume."
