
class Item:
    def __init__(self, index, downloaded = False):
        self.index = index
        self.downloaded = False


class Track(Item):
    def __init__(self, index, id, title, artists,album="", img="",release_date="", duration=-1, downloaded=False):
        super().__init__(index, downloaded)
        self.id = id
        self.title = title
        self.artists = artists
        self.album = album
        self.img = img
        self.release_date = release_date
        self.duration = duration

class Album(Item):
    def __init__(self, index, id, title,artists, total_tracks, release_date="", img="",downloaded=False):
        super().__init__(index)
        self.index = index
        self.id = id
        self.title = title
        self.artists = artists
        self.img = img
        self.total_tracks = total_tracks
        self.release_date = release_date
        self.index = index

class Artist(Item):
    def __init__(self,index, id, name, img="",downloaded=False):
        super().__init__(index)
        self.id = id
        self.name = name
        self.img = img
        self.index = index

class Playlist(Item):
    def __init__(self, index, id, title,creator, total_tracks, img="", downloaded=False):
        super().__init__(index)
        self.id = id
        self.title = title
        self.creator = creator
        self.total_tracks = total_tracks
        self.img=img
