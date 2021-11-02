import sys
import time
import requests
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThreadPool
from PyQt5.QtWidgets import (

    QApplication, QMainWindow, QDialog, QTreeWidget, QTreeWidgetItem, QFileDialog, QLineEdit

)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from librespot.audio.decoders import AudioQuality
from librespot.core import Session
from main_windowMedia import Ui_MainWindow
from login_dialog import Ui_LoginDialog
from zspotify import ZSpotify
from const import TRACK, NAME, ID, ARTIST, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUM, ALBUMS, \
    OWNER, PLAYLIST, PLAYLISTS, DISPLAY_NAME, PREMIUM, COVER_DEFAULT, DOWNLOAD_REAL_TIME, SEARCH_RESULTS,\
    DOWNLOADED, LIKED
from worker import Worker
from audio import MusicController, find_local_tracks, get_track_file_as_item
from download import DownloadController
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
        self.tabs = [TRACKS, ARTISTS, ALBUMS, PLAYLISTS]
        self.trees = [self.songsTree, self.artistsTree, self.albumsTree, self.playlistsTree]
        self.libraryTrees = [self.downloadedTree, self.likedTree]
        self.library = {DOWNLOADED:[], LIKED:[]}
        self.init_signals()
        self.init_info_labels()
        self.init_list_columns()
        self.init_results_amount_combo()
        self.init_downloads_view()
        self.music_controller = MusicController(self)
        self.download_controller = DownloadController(self)
        self.logged_in = False
        self.selected_item = None
        self.results = {}
        self.selected_tab = self.downloadedTab
        self.searchTabIndex = 1
        self.resultTabs.setCurrentIndex(0)
        self.on_tab_change(0)

    def show(self):
        super().show()
        if not ZSpotify.login():
            self.open_login_dialog()
        else:
            self.on_login_finished(1)

    def open_login_dialog(self):
        login_dialog = LoginDialog()
        login_dialog.finished.connect(self.on_login_finished)
        login_dialog.exec_()


    def on_login_finished(self, result):
        if result == 1:
            self.logged_in = True
            self.loginBtn.setEnabled(False)
            if ZSpotify.IS_PREMIUM:
                self.accountTypeLabel.setText("Premium Account")
                self.dlQualityLabel.setText("320kbps")
            else:
                self.accountTypeLabel.setText("Free Account")
                self.dlQualityLabel.setText("160kbps")
        self.login_dialog = None


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

        #clear all labels with no field and update rest to match visible tree view
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

    #run worker on thread that searches and return results through signal callback
    def send_search_input(self):
        if ZSpotify.SESSION:
            search = self.searchInput.text()
            worker = Worker(ZSpotify.search, search)
            worker.signals.result.connect(self.display_results)
            QThreadPool.globalInstance().start(worker)
            self.libraryTabs.setCurrentIndex(self.searchTabIndex)

        elif not self.logged_in:
            self.open_login_dialog()

    def display_results(self, results):
        self.results = results
        self.songsTree.clear()
        self.artistsTree.clear()
        self.albumsTree.clear()
        self.playlistsTree.clear()
        #Item details in QTreeWidgetItem must be in same order as their item tree
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


    def update_result_amount(self, index):
        amount = int(self.resultAmountCombo.itemText(index))
        ZSpotify.set_config(SEARCH_RESULTS, amount)


    def update_item_info(self, curr, old):
        item = None
        tab = ""
        try:
            i = int(curr.text(0))
            tab = self.tabs[self.resultTabs.currentIndex()]
            list = self.results[tab]
            item = list[i-1]
            self.selected_item = item
        except Exception as e:
            print(e)

        [lbl.setText("") for lbl in self.info_labels]
        if curr == None or curr.columnCount() <= 0: return
        for i in range(1,curr.columnCount()):
            if i < len(self.info_labels):
                self.info_labels[i-1].setText(curr.text(i))
                self.info_labels[i-1].setToolTip(curr.text(i))
        #if str(item.img) != "": self.load_album_cover(item.img)


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
        self.info_labels = [self.infoLabel1, self.infoLabel2, self.infoLabel3, self.infoLabel4, self.infoLabel5, self.infoLabel6]
        self.info_headers = [self.infoHeader1, self.infoHeader2, self.infoHeader3, self.infoHeader4, self.infoHeader5, self.infoHeader6]

    def init_signals(self):
        self.searchBtn.clicked.connect(self.send_search_input)
        self.searchInput.returnPressed.connect(self.send_search_input)
        self.resultTabs.currentChanged.connect(self.on_tab_change)
        for tree in self.trees:
            tree.currentItemChanged.connect(self.update_item_info)
        for tree in self.libraryTrees:
            tree.currentItemChanged.connect(self.update_item_info)
        self.loginBtn.clicked.connect(self.open_login_dialog)
        self.resultAmountCombo.currentIndexChanged.connect(self.update_result_amount)

    def init_downloads_view(self):
        track_files = find_local_tracks()
        self.library[DOWNLOADED] = []
        index = 0
        for file in track_files:
            track = get_track_file_as_item(file, index)
            if track != None:
                self.library[DOWNLOADED].append(track)
                item = QTreeWidgetItem([str(index),str(track.title), str(track.artists), str(track.album)])
                self.downloadedTree.addTopLevelItem(item)
                index += 1


    def init_results_amount_combo(self):
        amount = int(ZSpotify.get_config(SEARCH_RESULTS))
        nextHighest = 0
        for i in range(self.resultAmountCombo.count()):
            amt = int(self.resultAmountCombo.itemText(i))
            if amt == amount:
                self.resultAmountCombo.setCurrentIndex(i)
                return
            if amount < amt: nextHighest = i
        self.resultAmountCombo.insertItem(nextHighest)


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
