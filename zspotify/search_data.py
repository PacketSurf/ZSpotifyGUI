


class Track():
    def __init__(self, index, id, title, artists,album="", img="",release_date="", duration=-1,explicit=False):
        self.index = index
        self.id = id
        self.title = title
        self.artists = artists
        self.album = album
        self.img = img
        self.release_date = release_date
        self.duration = duration
        self.explicit = explicit
        self.index = index

class Album():
    def __init__(self, index, id, title,artists, total_tracks, release_date="", img="", explicit=False):
        self.index = index
        self.id = id
        self.title = title
        self.artists = artists
        self.img = img
        self.total_tracks = total_tracks
        self.release_date = release_date
        self.explicit = explicit
        self.index = index

class Artist():
    def __init__(self,index, id, name, img=""):
        self.index = index
        self.id = id
        self.name = name
        self.img = img
        self.index = index

class Playlist():
    def __init__(self, index, id, title,creator, total_tracks, img=""):
        self.index = index
        self.id = id
        self.title = title
        self.creator = creator
        self.total_tracks = total_tracks
        self.img=img
        self.index = index
