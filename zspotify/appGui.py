import sys
import requests
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (

    QApplication, QMainWindow, QDialog, QTreeWidget, QTreeWidgetItem, QFileDialog, QLineEdit

)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from librespot.audio.decoders import AudioQuality
from librespot.core import Session
from main_window import Ui_MainWindow
from login_dialog import Ui_LoginDialog
from zspotify import ZSpotify
from search_data import Artist
from const import TRACK, NAME, ID, ARTIST, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUM, ALBUMS, \
    OWNER, PLAYLIST, PLAYLISTS, DISPLAY_NAME, PREMIUM, COVER_DEFAULT, DOWNLOAD_REAL_TIME
from worker import DLWorker, SearchWorker
import qdarktheme


def main():
    ZSpotify.load_config()
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    win = Window()
    win.show()
    sys.exit(app.exec())


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.init_signals()
        self.init_tab_view()
        self.init_info_labels()
        self.init_list_columns()
        self.progressBar.hide()
        self.login_dialog = None
        self.selected_id = -1
        self.results = {}
        self.threads = []
        self.resultTabs.setCurrentIndex(0)
        self.on_tab_change(0)

    def show(self):
        super().show()
        self.open_login_dialog()

    def run_worker(self, worker, callback=None):
        thread = QThread()
        self.threads.append(thread)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)
        if callback: worker.finished.connect(callback)
        thread.start()

    def open_login_dialog(self):
        if not ZSpotify.login():
            self.login_dialog = LoginDialog()
            self.login_dialog.finished.connect(self.on_login_finished)
            self.login_dialog.exec_()
        else: self.on_login_finished(1)

    def on_login_finished(self, result):
        if result == 1:
            self.loginBtn.setEnabled(False)
            if ZSpotify.IS_PREMIUM:
                self.accountTypeLabel.setText("Premium Account")
                self.dlQualityLabel.setText("320kbps")
            else:
                self.accountTypeLabel.setText("Free Account")
                self.dlQualityLabel.setText("160kbps")
        self.login_dialog = None

    def on_start_download(self):
        if self.selected_id == -1: return
        self.progressBar.setValue(0)
        self.progressBar.setEnabled(True)
        self.progressBar.show()
        item = self.get_item(self.selected_id)
        if item != None:
            if type(item) == Artist:
                self.downloadInfoLabel.setText(f"Downloading {item.name} albums...")
            else:
                self.downloadInfoLabel.setText(f"Downloading {item.title}...")
        self.downloadBtn.setEnabled(False)
        tab = self.resultTabs.currentIndex()
        self.dl_worker = DLWorker(self.selected_id, self.tabs[tab])
        self.dl_worker.update.connect(self.update_dl_progress)
        self.run_worker(self.dl_worker, self.on_download_complete)


    def on_download_complete(self):
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.downloadInfoLabel.setText("")
        self.downloadBtn.setEnabled(True)
        QApplication.processEvents()

    def update_dl_progress(self, amount):
        perc = int(amount*100)
        self.progressBar.setValue(perc)
        self.progressBar.show()
        QApplication.processEvents()

    def on_tab_change(self, index):
        if self.tabs and index < len(self.tabs) and index > 0:
            if self.tabs[index] == TRACKS:
                self.downloadBtn.setText("Download")
            if self.tabs[index] == ARTISTS:
                self.downloadBtn.setText("Download all albums")
            if self.tabs[index] == ALBUMS:
                self.downloadBtn.setText("Download album")
            if self.tabs[index] == PLAYLISTS:
                self.downloadBtn.setText("Download playlist")
        else: self.downloadBtn.setText("Download")

        i = self.resultTabs.currentIndex()
        tree = self.trees[i]
        header = tree.headerItem()
        for i in range(0,len(self.info_headers)):
            self.info_labels[i].setText("")
            if i < tree.columnCount()-1:
                self.info_headers[i].setText(f"{header.text(i+1)}:")
            else:
                self.info_headers[i].setText("")

        self.load_album_cover()

    def send_search_input(self):
        if ZSpotify.SESSION:
            search = self.searchInput.text()
            self.search_worker = SearchWorker(search)
            self.run_worker(self.search_worker, callback=self.display_results)

        elif self.login_dialog is None:
            self.open_login_dialog()


    def display_results(self, results):
        self.results = results
        self.songsTree.clear()
        self.artistsTree.clear()
        self.albumsTree.clear()
        self.playlistsTree.clear()

        try:
            for track in self.results[TRACKS]:
                item = QTreeWidgetItem([str(track.index), track.title, track.artists, track.album, str(track.duration), track.release_date])
                self.songsTree.addTopLevelItem(item)
            for artist in self.results[ARTISTS]:
                item = QTreeWidgetItem([str(artist.index), artist.name])
                self.artistsTree.addTopLevelItem(item)
            for album in self.results[ALBUMS]:
                item = QTreeWidgetItem([str(album.index), album.title, album.artists, str(album.total_tracks), str(album.release_date)])
                self.albumsTree.addTopLevelItem(item)
            for playlist in self.results[PLAYLISTS]:
                item = QTreeWidgetItem([str(playlist.index), playlist.title, str(playlist.creator), str(playlist.total_tracks)])
                self.playlistsTree.addTopLevelItem(item)
        except Exception:
            pass

    def update_item_info(self, curr, old):
        item = None
        tab = ""
        try:
            i = int(curr.text(0))
            tab = self.tabs[self.resultTabs.currentIndex()]
            list = self.results[tab]
            item = list[i-1]
            self.selected_id = item.id
        except Exception as e:
            print(e)

        [lbl.setText("") for lbl in self.info_labels]
        if curr == None or curr.columnCount() <= 0: return
        for i in range(1,curr.columnCount()):
            if i < len(self.info_labels):
                self.info_labels[i-1].setText(curr.text(i))
                self.info_labels[i-1].setToolTip(curr.text(i))
        self.load_album_cover(item.img)


    def load_album_cover(self, url=""):
        lbl = self.coverArtLabel
        pixmap = QPixmap(COVER_DEFAULT)
        if url != "":
            image = QImage()
            image.loadFromData(requests.get(url).content)
            pixmap = QPixmap(image)
        lbl.setPixmap(pixmap)
        lbl.setScaledContents(True)
        lbl.show()

    def change_dl_dir(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            dir = dialog.selectedFiles()
            ZSpotify.set_config("ROOT_PATH", dir[0])

    #0 for off, 1 for on
    def set_real_time_dl(self, value):
        if value == 0:
            ZSpotify.set_config("DOWNLOAD_REAL_TIME", False)
        else:
            ZSpotify.set_config("DOWNLOAD_REAL_TIME", True)




    def get_item(self, id):
        if self.results == {}: return
        i = self.resultTabs.currentIndex()
        tab = self.tabs[i]
        for item in self.results[tab]:
            if item.id == id:
                return item
        return None

    def init_list_columns(self):
        #Resize duration header in songs tree
        self.songsTree.header().resizeSection(4,65)
        for tree in self.trees:
            #Resize index header in all trees
            tree.header().resizeSection(0, 65)

    def init_info_labels(self):
        dl_realtime = ZSpotify.get_config("DOWNLOAD_REAL_TIME")
        self.realTimeCheckBox.setChecked(dl_realtime)
        self.info_labels = [self.infoLabel1, self.infoLabel2, self.infoLabel3, self.infoLabel4, self.infoLabel5, self.infoLabel6]
        self.info_headers = [self.infoHeader1, self.infoHeader2, self.infoHeader3, self.infoHeader4, self.infoHeader5, self.infoHeader6]

    def init_signals(self):
        self.searchBtn.clicked.connect(self.send_search_input)
        self.searchInput.returnPressed.connect(self.send_search_input)
        self.downloadBtn.clicked.connect(self.on_start_download)
        self.resultTabs.currentChanged.connect(self.on_tab_change)
        self.songsTree.currentItemChanged.connect(self.update_item_info)
        self.artistsTree.currentItemChanged.connect(self.update_item_info)
        self.albumsTree.currentItemChanged.connect(self.update_item_info)
        self.playlistsTree.currentItemChanged.connect(self.update_item_info)
        self.dirBtn.clicked.connect(self.change_dl_dir)
        self.loginBtn.clicked.connect(self.open_login_dialog)
        self.realTimeCheckBox.stateChanged.connect(self.set_real_time_dl)

    def init_tab_view(self):
        self.tabs = [TRACKS, ARTISTS, ALBUMS, PLAYLISTS]
        self.trees = [self.songsTree, self.artistsTree, self.albumsTree, self.playlistsTree]


class LoginDialog(QDialog, Ui_LoginDialog):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.init_signals()
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

    def send_login(self):
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        if ZSpotify.login(username, password):
            self.accept()
        else: self.try_again_text()

    def try_again_text(self):
        self.loginInfoLabel.setText("Incorrect username/password.")

    def init_signals(self):
        self.loginBtn.clicked.connect(self.send_login)
        self.cancelBtn.clicked.connect(self.reject)





if __name__ == "__main__":
    main()
