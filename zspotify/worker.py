from PyQt5.QtCore import QObject, pyqtSignal
from zspotify import ZSpotify
from playlist import download_playlist
from album import download_album, download_artist_albums
from track import download_track
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS

class Worker(QObject):
    failed = pyqtSignal()

    def run(self):
        pass

class SearchWorker(Worker):
    finished = pyqtSignal(dict)

    def __init__(self, search_input):
        super().__init__()
        self.search_input = search_input

    def run(self):
        try:
            results = ZSpotify.search(self.search_input)
            self.finished.emit(results)
        except:
            self.failed.emit()

class DLWorker(Worker):
    finished = pyqtSignal()
    update = pyqtSignal(float, int)

    def __init__(self, id, dl_type):
        super().__init__()
        self.id = id
        self.dl_type = dl_type

    def run(self):
        try:
            if self.dl_type == TRACKS:
                download_track(self.id,progress_callback=self.update.emit)
            elif self.dl_type == ALBUMS:
                download_album(self.id, progress_callback=self.update.emit)
            elif self.dl_type == ARTISTS:
                download_artist_albums(self.id)
            elif self.dl_type == PLAYLISTS:
                download_playlist(self.id,progress_callback=self.update.emit)
        except:
            self.failed.emit()
        self.finished.emit()
