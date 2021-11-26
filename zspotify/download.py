import logging
from zspotify import ZSpotify
from playlist import download_playlist
from album import download_album, download_artist_albums
from track import DownloadStatus, download_track
from item import Item, Track, Artist, Album, Playlist
from worker import Worker
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS, FORMATS, DIR_ICON
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog
from view import set_button_icon
from config import Config, ROOT_PATH, DOWNLOAD_FORMAT, DOWNLOAD_REAL_TIME
logger = logging.getLogger(__name__)

class DownloadController(QObject):

    downloadComplete = pyqtSignal(Item)
    downloadDirChanged = pyqtSignal()

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.window.progressBar.hide()
        dl_realtime = Config.get_download_real_time()
        self.window.realTimeCheckBox.setChecked(dl_realtime)
        self.load_download_format()
        self.init_signals()
        self.item = None
        self.downloading = False
        self.download_queue = []
        set_button_icon(self.window.dirBtn, DIR_ICON)


    def on_click_download(self):
        if self.window.selected_item:
            if self.window.selected_item in self.download_queue:
                self.download_queue.remove(self.window.selected_item)
                self.update_download_view(self.window.selected_item)
                self.update_dl_queue_combo()
                return
            else:
                self.download_queue.append(self.window.selected_item)
                self.update_dl_queue_combo()
                self.update_download_view(self.window.selected_item)
        if not self.downloading and not self.item == self.download_queue[0]:
            self.start_download(self.download_queue[0])

    def start_download(self, item):
        self.item = item
        self.downloading = True
        self.window.progressBar.setValue(0)
        self.window.progressBar.setEnabled(True)
        self.window.progressBar.show()
        dl_info = self.get_item_info_string(item)
        self.window.downloadInfoLabel.setText(f"Downloading: {dl_info}")
        tab = self.window.searchTabs.currentIndex()
        worker = Worker(self.download_item, item, update=self.update_dl_progress)
        worker.signals.result.connect(self.on_download_complete)
        worker.signals.error.connect(self.window.on_api_error)
        QThreadPool.globalInstance().start(worker)


    def download_item(self, signal, *args, **kwargs):
        if len(args) <= 0 or args[0] == None: return
        self.item = args[0]
        try:
            status = DownloadStatus.FAILED
            if type(self.item) == Track:
                status = download_track(self.item.id,progress_callback=signal)
            elif type(self.item) == Album:
                status = download_album(self.item.id, progress_callback=signal)
            elif type(self.item) == Artist:
                status = download_artist_albums(self.item.id, progress_callback=signal)
            elif type(self.item) == Playlist:
                status = download_playlist(self.item.id,progress_callback=signal)
            return status
        except Exception as e:
            logger.error(e)
            print(e)
            return DownloadStatus.FAILED

    def on_download_complete(self, status):
        if status and status.value == DownloadStatus.FAILED.value:
            self.window.on_api_error()
        self.window.progressBar.setValue(0)
        self.window.progressBar.hide()
        self.window.downloadInfoLabel.setText("")
        self.window.downloadBtn.setEnabled(True)
        self.download_queue.pop(0)
        self.update_dl_queue_combo()
        if self.item != None:
            if status and status.value == DownloadStatus.SUCCESS.value:
                self.item.downloaded = True
                self.downloadComplete.emit(self.item)
        self.item = None
        self.downloading = False
        if self.window.selected_item:
            self.update_download_view(self.window.selected_item)
        QApplication.processEvents()
        if len(self.download_queue) > 0:
            self.start_download(self.download_queue[0])

    def update_dl_progress(self, amount):
        perc = int(amount*100)
        self.window.progressBar.setValue(perc)
        self.window.progressBar.show()
        QApplication.processEvents()

    def update_dl_queue_combo(self):
        self.window.downloadQueueCombo.clear()
        items = []
        for item in self.download_queue:
            text = self.get_item_info_string(item)
            items.append(text)
        items.reverse()
        self.window.downloadQueueCombo.addItems(items)

    def change_dl_dir(self):
        dialog = QFileDialog(self.window)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setDirectory(Config.get_root_path())
        if dialog.exec_():
            dir = dialog.selectedFiles()
            if len(dir) > 0:
                Config.set(ROOT_PATH, dir[0])
                self.downloadDirChanged.emit()

    def update_download_format(self, index):
        format = self.window.fileFormatCombo.itemText(index)
        Config.set(DOWNLOAD_FORMAT, format)

    def load_download_format(self):
        self.window.fileFormatCombo.clear()
        format = Config.get_download_format()
        self.window.fileFormatCombo.addItems(FORMATS)
        for i in range(len(FORMATS)):
            if format == FORMATS[i]:
                self.window.fileFormatCombo.setCurrentIndex(i)
                return
        self.window.fileFormatCombo.setCurrentIndex(0)
        Config.set(DOWNLOAD_FORMAT, FORMATS[0])

    def set_real_time_dl(self, value):
        if value == 0:
            print('nice')
            Config.set(DOWNLOAD_REAL_TIME, False)
        else:
            Config.set(DOWNLOAD_REAL_TIME, True)

    def update_download_view(self, item):
        if item.downloaded:
            self.window.downloadBtn.setEnabled(False)
            self.window.downloadBtn.setText("Downloaded")
            return
        elif len(self.download_queue) > 0:
            self.window.downloadBtn.setEnabled(True)
            if item in self.download_queue:
                if self.download_queue[0] == item:
                    self.window.downloadBtn.setText("Downloading")
                    self.window.downloadBtn.setEnabled(False)
                else:
                    self.window.downloadBtn.setText("Remove From Queue")
                return
            self.window.downloadBtn.setText("Queue track")
            if type(item) == Artist:
                self.window.downloadBtn.setText("Queue Artist Albums")
            elif type(item) == Album:
                self.window.downloadBtn.setText("Queue Album")
            elif type(item) == Playlist:
                self.window.downloadBtn.setText("Queue Playlist")
        else:
            self.window.downloadBtn.setEnabled(True)
            self.window.downloadBtn.setText("Download")
            if type(item) == Artist:
                self.window.downloadBtn.setText("Download All Albums")
            elif type(item) == Album:
                self.window.downloadBtn.setText("Download Album")
            elif type(item) == Playlist:
                self.window.downloadBtn.setText("Download Playlist")

    def get_item_info_string(self, item):
        info = ""
        if "title" in item.__dict__.keys():
            info += f"{item.title} - "
        if "name" in item.__dict__.keys():
            info += f"{item.name} - "
        if "artists" in item.__dict__.keys():
            info += item.artists
        return info

    def init_signals(self):
        self.window.downloadBtn.clicked.connect(self.on_click_download)
        self.window.dirBtn.clicked.connect(self.change_dl_dir)
        self.window.realTimeCheckBox.stateChanged.connect(self.set_real_time_dl)
        self.window.fileFormatCombo.currentIndexChanged.connect(self.update_download_format)
