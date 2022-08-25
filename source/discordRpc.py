from pypresence import Presence
import threading
import time
from config import Config


class RPC:
    def __init__(self):
        self.app_id = Config.get_discord_rpc_app_id()
        self.rpc = Presence(self.app_id)
        self.rpc.connect()
        self.set_rpc_activity(**{
            "details":     "Not currently playing",
            "state":       "any music",
            "large_image": "zsplogo",
            "large_text":  "ZSpotify"
        })

    def set_rpc_activity(self, **kwargs):
        self.rpc.update(**kwargs)

    def set_rpc_to_item(self, item):
        details = "Unknown"
        state = ""
        if "title" in dir(item):
            details = item.title
        if "artists" in dir(item):
            state = item.artists
        if "album" in dir(item):
            if "artists" in dir(item):
                state += " - " + item.title
            else:
                state = item.album
        if state == "":
            state = "Unknown"

        self.set_rpc_activity(**{
            "details":     details,
            "state":       state,
            "large_image": "zsplogo",
            "large_text":  "ZSpotify"
        })
