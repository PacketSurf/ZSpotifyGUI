from zspotify import ZSpotify
from playlist import download_playlist
from album import download_album, download_artist_albums
from track import download_track
from item import Item, Track, Artist, Album, Playlist
from worker import Worker
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS, ROOT_PATH, DOWNLOAD_REAL_TIME
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

class DownloadController(QObject):

    downloadComplete = pyqtSignal(Item)

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.window.progressBar.hide()
        dl_realtime = ZSpotify.get_config(DOWNLOAD_REAL_TIME)
        self.window.realTimeCheckBox.setChecked(dl_realtime)
        self.init_signals()
        self.item = None
        self.downloading = False

    def on_start_download(self):
        item = self.window.selected_item
        if self.downloading or item == None: return
        self.downloading = True
        self.window.progressBar.setValue(0)
        self.window.progressBar.setEnabled(True)
        self.window.progressBar.show()

        if type(item) == Artist:
            self.window.downloadInfoLabel.setText(f"Downloading {item.name} albums...")
        else:
            self.window.downloadInfoLabel.setText(f"Downloading {item.title}...")
        self.window.downloadBtn.setEnabled(False)
        tab = self.window.resultTabs.currentIndex()
        worker = Worker(self.download_item, item, update=self.update_dl_progress)
        worker.signals.finished.connect(self.on_download_complete)
        QThreadPool.globalInstance().start(worker)


    def download_item(self, signal, *args, **kwargs):
        if len(args) <= 0 or args[0] == None: return
        self.item = args[0]
        try:
            if type(self.item) == Track:
                download_track(self.item.id,progress_callback=signal)
            elif type(self.item) == Album:
                download_album(self.item.id, progress_callback=signal)
            elif type(self.item) == Artist:
                download_artist_albums(self.item.id)
            elif type(self.item) == Playlist:
                download_playlist(self.item.id,progress_callback=signal)
        except Exception as e:
            print(e)


    def on_download_complete(self):
        self.window.progressBar.setValue(0)
        self.window.progressBar.hide()
        self.window.downloadInfoLabel.setText("")
        self.window.downloadBtn.setEnabled(True)
        if self.item != None:
            self.item.downloaded = True
            self.downloadComplete.emit(self.item)
        self.item = None
        self.downloading = False
        QApplication.processEvents()

    def update_dl_progress(self, amount):
        perc = int(amount*100)
        self.window.progressBar.setValue(perc)
        self.window.progressBar.show()
        QApplication.processEvents()

    def change_dl_dir(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            dir = dialog.selectedFiles()
            ZSpotify.set_config(ROOT_PATH, dir[0])

        #0 for off, 1 for on
    def set_real_time_dl(self, value):
        if value == 0:
            ZSpotify.set_config(DOWNLOAD_REAL_TIME, False)
        else:
            ZSpotify.set_config(DOWNLOAD_REAL_TIME, True)

    def init_signals(self):
        self.window.downloadBtn.clicked.connect(self.on_start_download)
        self.window.dirBtn.clicked.connect(self.change_dl_dir)
        self.window.realTimeCheckBox.stateChanged.connect(self.set_real_time_dl)
