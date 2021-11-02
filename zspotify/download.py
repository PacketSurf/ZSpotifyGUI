from zspotify import ZSpotify
from const import TRACKS, ALBUMS, ARTISTS, PLAYLISTS, DOWNLOAD_REAL_TIME, ROOT_PATH
from playlist import download_playlist
from album import download_album, download_artist_albums
from track import download_track
from worker import Worker
from search_data import Artist
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication

class DownloadController:
    def __init__(self, window):
        self.window = window
        self.window.progressBar.hide()
        dl_realtime = ZSpotify.get_config(DOWNLOAD_REAL_TIME)
        self.window.realTimeCheckBox.setChecked(dl_realtime)
        self.init_signals()

    def on_start_download(self):
        item = self.window.selected_item
        if item == None: return
        self.window.progressBar.setValue(0)
        self.window.progressBar.setEnabled(True)
        self.window.progressBar.show()
        if type(item) == Artist:
            self.window.downloadInfoLabel.setText(f"Downloading {item.name} albums...")
        else:
            self.window.downloadInfoLabel.setText(f"Downloading {item.title}...")
        self.window.downloadBtn.setEnabled(False)
        tab = self.window.resultTabs.currentIndex()
    
        worker = Worker(self.download_item, item.id, update=self.update_dl_progress)
        worker.signals.finished.connect(self.on_download_complete)
        QThreadPool.globalInstance().start(worker)


    def download_item(self, signal, *args, **kwargs):
        item_id = args[0]
        index = self.window.resultTabs.currentIndex()
        if self.window.tabs[index] == TRACKS:
            download_track(item_id,progress_callback=signal)
        elif self.window.tabs[index] == ALBUMS:
            download_album(item_id, progress_callback=signal)
        elif self.window.tabs[index] == ARTISTS:
            download_artist_albums(item_id)
        elif self.window.tabs[index] == PLAYLISTS:
            download_playlist(item_id,progress_callback=signal)


    def on_download_complete(self):
        self.window.progressBar.setValue(0)
        self.window.progressBar.hide()
        self.window.downloadInfoLabel.setText("")
        self.window.downloadBtn.setEnabled(True)
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
        self.window.realTimeCheckBox.stateChanged.connect(self.set_real_time_dl)
        self.window.dirBtn.clicked.connect(self.change_dl_dir)
