from const import TRACK, ALBUM, ARTIST, PLAYLIST, SPOTIFY_URL
from utils import set_audio_tags


class Item:
    def __init__(self, index, downloaded=False, path="", _type="", ID=""):
        self.type = _type
        self.index = index
        self.downloaded = downloaded
        self.path = path
        self.id = ID if ID else ""
        self.url = f"{SPOTIFY_URL}{_type}/{ID}" if ID and _type else ""


class Track(Item):
    def __init__(self, index, ID, title, artists, album="", img="", release_date="", duration=-1, disc_number=-1,
                 track_number=1, album_id="", downloaded=False, path=""):
        super().__init__(index, downloaded, path, TRACK, ID)
        self.title = title
        self.artists = artists
        self.album = album
        self.img = img
        self.release_date = release_date
        self.duration = duration
        self.disc_number = disc_number
        self.track_number = track_number
        self.album_id = album_id
        self.album_url = "" if self.album_id == "" else f"{SPOTIFY_URL}{ALBUM}/{self.album_id}"

    def update_meta_tags(self):
        set_audio_tags(self.path, str(self.artists), self.title, self.album,
                       disc_number=self.disc_number, track_number=self.track_number, spotify_id=self.id,
                       album_id=self.album_id, img=self.img)


class Album(Item):
    def __init__(self, index, ID, title, artists, total_tracks, release_date="", img="", downloaded=False, path=""):
        super().__init__(index, downloaded, path, ALBUM, ID)
        self.title = title
        self.artists = artists
        self.img = img
        self.total_tracks = total_tracks
        self.release_date = release_date
        self.index = index


class Artist(Item):
    def __init__(self,index, ID, name, img="", downloaded=False, path=""):
        super().__init__(index, downloaded, path, ARTIST, ID)
        self.name = name
        self.img = img
        self.index = index


class Playlist(Item):
    def __init__(self, index, ID, title, creator, total_tracks, img="", downloaded=False, path=""):
        super().__init__(index, downloaded, path, PLAYLIST, ID)
        self.title = title
        self.creator = creator
        self.total_tracks = total_tracks
        self.img = img
