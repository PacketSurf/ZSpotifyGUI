"""
ZSpotifyGUI
It's like youtube-dl, but for Spotify.

(GUI made by PacketSurf - github.com/PacketSurf)
(ZSpotify made by Deathmonger/Footsiefat - @doomslayer117:matrix.org | github.com/Footsiefat)
"""

import sys
import requests
import logging
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeWidgetItem, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from main_window import Ui_MainWindow
from login_dialog import Ui_LoginDialog
from zspotify import ZSpotify
from config import Config, TOTAL_SEARCH_RESULTS
from const import ARTISTS, TRACKS, ALBUMS, PLAYLISTS, COVER_DEFAULT, \
    DOWNLOADED, LIKED, SAVED_TRACKS_URL, LOG_FILE, LOGO_BANNER
from worker import Worker
from audio import MusicController, find_local_tracks, get_track_file_as_item
from download import DownloadController
from track import play_track, get_cover_art
import qdarktheme
from itemTree import ItemTree
from item import Track, Artist, Album, Playlist
from view import set_button_icon, set_label_image

logging.basicConfig(level=logging.INFO, filename=LOG_FILE,
                    format='%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')


def main():
    Config.load()
    app = QApplication(sys.argv)
    app.setApplicationName("ZSpotify")
    app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    win = Window()
    win.show()
    sys.exit(app.exec())


class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        set_label_image(self.bannerLabel, LOGO_BANNER)
        self.libraryTabList = ["Downloaded", "Liked"]
        self.searchTabList = [TRACKS, ARTISTS, ALBUMS, PLAYLISTS]
        self.library = {DOWNLOADED: [], LIKED: []}
        self.init_info_labels()
        self.init_tree_views()
        self.init_results_amount_combo()
        self.init_downloads_view()
        set_label_image(self.coverArtLabel, COVER_DEFAULT)
        self.tabs = [self.library_trees, self.search_trees, self.queue_trees]
        self.tabWidgets = [self.libraryTabs, self.searchTabs, self.queueTabs]
        try:
            self.music_controller = MusicController(self)
        except Exception as e:
            logging.critical(e)
        self.download_controller = DownloadController(self)
        self.init_signals()
        self.logged_in = False
        self.selected_item = None
        self.results = {}
        self.selected_tab = self.download_tree
        self.searchTabIndex = 1
        self.searchTabs.setCurrentIndex(0)
        self.musicTabs.setCurrentIndex(0)
        self.libraryTabs.setCurrentIndex(0)
        self.download_tree.focus()
        self.reconnecting = False

    def show(self):
        super().show()
        if not ZSpotify.login():
            self.open_login_dialog()
        else:
            self.on_login_finished(1)

    def on_click_login(self):
        if self.logged_in:
            ZSpotify.logout()
            self.loginBtn.setText("Login")
        self.open_login_dialog()

    def open_login_dialog(self):
        login_dialog = LoginDialog()
        login_dialog.finished.connect(self.on_login_finished)
        login_dialog.exec_()

    def on_login_finished(self, result):
        if result == 1:
            self.logged_in = True
            self.loginBtn.setText("Logout")
            if ZSpotify.IS_PREMIUM:
                self.accountTypeLabel.setText("Premium Account")
                self.dlQualityLabel.setText("320kbps")
            else:
                self.accountTypeLabel.setText("Free Account")
                self.dlQualityLabel.setText("160kbps")
        self.login_dialog = None

    def on_tab_change(self, index):
        i = self.musicTabs.currentIndex()
        library = self.tabs[i]
        self.selected_tab = library[index]
        self.selected_tab.load_content()
        self.selected_tab.focus()

    def on_music_tab_change(self, index):
        tabs = self.tabs[index]
        i = self.tabWidgets[index].currentIndex()
        self.selected_tab = tabs[i]
        self.selected_tab.load_content()
        self.selected_tab.focus()

    # run worker on thread that searches and return results through signal callback
    def send_search_input(self):
        if ZSpotify.SESSION:
            search = self.searchInput.text()
            worker = Worker(ZSpotify.search, search)
            worker.signals.result.connect(self.display_results)
            worker.signals.error.connect(self.on_api_error)
            QThreadPool.globalInstance().start(worker)
            self.musicTabs.setCurrentIndex(1)
            self.searchTabs.setCurrentIndex(0)
        elif not self.logged_in:
            self.open_login_dialog()

    def display_results(self, results):
        self.selected_tab.focus()
        self.results = results
        self.songs_tree.set_items(results[TRACKS])
        self.artists_tree.set_items(results[ARTISTS])
        self.albums_tree.set_items(results[ALBUMS])
        self.playlists_tree.set_items(results[PLAYLISTS])

    def update_item_info(self, item, headers, labels):
        if not item: return
        self.selected_item = item
        worker = Worker(self._cover_art_loader, item)
        QThreadPool.globalInstance().start(worker)
        [lbl.setText("") for lbl in self.info_labels]
        if "Index" in headers:
            labels.pop(headers.index("Index"))
            headers.remove("Index")
        for i in range(len(self.info_labels)):
            if i < len(labels):
                self.info_labels[i].setText(labels[i])
                self.info_labels[i].setToolTip(labels[i])
            else:
                self.info_labels[i].setText("")
                self.info_labels[i].setToolTip("")
        self.download_controller.update_download_view(item)

    def update_item_labels(self, headers):
        set_label_image(self.coverArtLabel, COVER_DEFAULT)
        if "Index" in headers: headers.remove("Index")
        for i in range(len(self.info_headers)):
            if i < len(self.info_labels):
                self.info_labels[i].setText("")
                self.info_labels[i].setToolTip("")
            if i < len(headers):
                self.info_headers[i].setText(f"{headers[i]}:")
            else:
                self.info_headers[i].setText("")

    # Does network call, be careful (Run in worker thread instead)
    def request_cover_art(self, url):
        lbl = self.coverArtLabel
        pixmap = QPixmap(COVER_DEFAULT)
        if url != "":
            image = QImage()
            image.loadFromData(requests.get(url).content)
            pixmap = QPixmap(image)
        lbl.setPixmap(pixmap)
        lbl.setScaledContents(True)
        lbl.show()

    def update_result_amount(self, index):
        amount = int(self.resultAmountCombo.itemText(index))
        Config.set(TOTAL_SEARCH_RESULTS, amount)

    def select_next_item(self, current_item=None, tree=None):
        if not tree: tree = self.selected_tab
        if current_item:
            index = tree.item_index(current_item)
        else:
            index = tree.current_item_index()
        if index == -1: return None
        if index == tree.count():
            index = 0
        else:
            index += 1
        return tree.select_index(index)

    def select_prev_item(self, current_item=None, tree=None):
        if not tree: tree = self.selected_tab
        if current_item:
            index = tree.item_index(current_item)
        else:
            index = tree.current_item_index()
        if index == -1: return None
        if index <= 0:
            index = tree.count()
        else:
            index -= 1
        return tree.select_index(index)

    def init_info_labels(self):
        self.info_labels = [self.infoLabel1, self.infoLabel2, self.infoLabel3, self.infoLabel4, self.infoLabel5,
                            self.infoLabel6]
        self.info_headers = [self.infoHeader1, self.infoHeader2, self.infoHeader3, self.infoHeader4, self.infoHeader5,
                             self.infoHeader6]

    def init_signals(self):
        self.searchBtn.clicked.connect(self.send_search_input)
        self.searchInput.returnPressed.connect(self.send_search_input)
        self.musicTabs.currentChanged.connect(self.on_music_tab_change)
        self.searchTabs.currentChanged.connect(self.on_tab_change)
        self.libraryTabs.currentChanged.connect(self.on_tab_change)
        self.queueTabs.currentChanged.connect(self.on_tab_change)
        self.loginBtn.clicked.connect(self.on_click_login)
        self.resultAmountCombo.currentIndexChanged.connect(self.update_result_amount)
        self.download_controller.downloadComplete.connect(self.init_downloads_view)
        self.download_controller.downloadDirChanged.connect(self.init_downloads_view)
        self.listenQueueBtn.clicked.connect(self.show_queue_view)
        self.music_controller.onPlay.connect(self.queue_tree.load_function)
        for tree in self.trees:
            if tree == self.queue_tree:
                tree.signals.doubleClicked.connect(self.music_controller.on_play_queue_song)
            tree.signals.itemChanged.connect(self.update_item_info)
            tree.signals.onSelected.connect(self.update_item_labels)
            tree.signals.doubleClicked.connect(self.on_try_play_item)
            tree.signals.onListenQueued.connect(self.music_controller.queue_track)
            tree.signals.onDownloadQueued.connect(self.download_controller.on_click_download)
            return_shortcut = QtWidgets.QShortcut(QtCore.Qt.Key_Return,
                                                  tree.tree,
                                                  context=QtCore.Qt.WidgetShortcut,
                                                  activated=self.on_try_play_item)

            space_shortcut = QtWidgets.QShortcut(QtCore.Qt.Key_Space,
                                                 tree.tree,
                                                 context=QtCore.Qt.WidgetShortcut,
                                                 activated=self.on_press_space_item)

    def on_try_play_item(self):
        item = self.selected_tab.get_selected_item()
        if item and self.selected_tab.can_play:
            self.music_controller.play(item, self.selected_tab)

    def on_press_space_item(self):
        item = self.selected_tab.get_selected_item()
        if item: self.music_controller.on_press_play()

    def on_press_tab(self):
        i = self.libraryTabs.getCurrentIndex()
        i += 1
        if i >= self.libraryTabs.count(): i = 0
        self.libraryTabs.setCurrentIndex(i)

    def on_api_error(self):
        self.logged_in = False
        if self.reconnecting: return
        worker = Worker(ZSpotify.login)
        worker.signals.result.connect(self.api_reconnect_complete)
        self.reconnecting = True
        QThreadPool.globalInstance().start(worker)

    def api_reconnect_complete(self, success):
        self.reconnecting = False
        logging.info("Attempting to reconnect to spotify.")
        print("Attempting to reconnect to spotify.")
        if success:
            logging.info("Reconnected to spotify.")
            print("Reconnected to zspotify.")
        else:
            logging.error("Failed to reconnect to spotify.")
            print("Failed to reconnect to spotify.")

    def init_liked_view(self):
        worker = Worker(ZSpotify.load_tracks_url, SAVED_TRACKS_URL)
        worker.signals.result.connect(self.liked_view_result_handle)
        QThreadPool.globalInstance().start(worker)

    def liked_view_result_handle(self, items):
        for item in items:
            if item in self.liked_tree.items:
                continue
            else:
                self.liked_tree.set_items(items)

    def init_downloads_view(self):
        try:
            track_files = find_local_tracks()
            self.library[DOWNLOADED] = []
            index = 0
            self.download_tree.clear()
            for file in track_files:
                track = get_track_file_as_item(file, index)
                if track:
                    self.library[DOWNLOADED].append(track)
                    self.download_tree.add_item(track)
                    index += 1
        except Exception as e:
            logging.error(e)

    def init_queue_view(self):
        if not self.music_controller: return
        queue = self.music_controller.listen_queue.copy()
        queue += self.music_controller.shuffle_queue
        self.queue_tree.set_items(queue)

    def show_queue_view(self):
        self.musicTabs.setCurrentIndex(2)
        self.queueTabs.setCurrentIndex(0)

    def init_results_amount_combo(self):
        amount = int(Config.get_total_search_results())
        nextHighest = 0
        for i in range(self.resultAmountCombo.count()):
            amt = int(self.resultAmountCombo.itemText(i))
            if amt == amount:
                self.resultAmountCombo.setCurrentIndex(i)
                return
            if amount < amt: nextHighest = i
        self.resultAmountCombo.insertItem(nextHighest)

    # Defines the information displayed in song tree headers, the QTreeWidgetItem lamba must
    # have variables that match the header text given in the next line
    def init_tree_views(self):
        self.songs_tree = ItemTree(self.songsTree)
        self.songs_tree.set_header_item(
            Track("Index", 0, "Title", "Artists", "Album", duration="Duration", release_date="Release Date"))

        self.artists_tree = ItemTree(self.artistsTree, lambda artist: QTreeWidgetItem([str(artist.index), artist.name]))
        self.artists_tree.set_header_item(Artist("Index", 0, "Name"))

        self.albums_tree = ItemTree(self.albumsTree,
                                    lambda album: QTreeWidgetItem([str(album.index), album.title, album.artists, \
                                                                   str(album.total_tracks), str(album.release_date)]))
        self.albums_tree.set_header_item(Album("Index", 0, "Title", "Artists", "Total Tracks", "Release Date"))

        self.playlists_tree = ItemTree(self.playlistsTree,
                                       lambda playlist: QTreeWidgetItem([str(playlist.index), playlist.title, \
                                                                         str(playlist.creator),
                                                                         str(playlist.total_tracks)]))
        self.playlists_tree.set_header_item(Playlist("Index", 0, "Title", "Author", "Total Tracks"))

        self.download_tree = ItemTree(self.downloadedTree,
                                      lambda track: QTreeWidgetItem([track.title, track.artists, track.album]))
        self.download_tree.set_header_item(Track("", 0, "Title", "Artists", "Albums"))

        self.liked_tree = ItemTree(self.likedTree,
                                   lambda track: QTreeWidgetItem([track.title, track.artists, track.album]))
        self.liked_tree.set_header_item(Track("", 0, "Title", "Artists", "Albums"))
        self.liked_tree.load_function = self.init_liked_view

        self.queue_tree = ItemTree(self.queueTree,
                                   lambda track: QTreeWidgetItem([track.title, track.artists, track.album]), False)
        self.queue_tree.set_header_item(Track("", 0, "Title", "Artists", "Albums"))
        self.queue_tree.load_function = self.init_queue_view

        self.search_trees = [self.songs_tree, self.artists_tree, self.albums_tree, self.playlists_tree]
        self.library_trees = [self.download_tree, self.liked_tree]
        self.queue_trees = [self.queue_tree]
        self.trees = [self.songs_tree, self.artists_tree, self.albums_tree, self.playlists_tree, \
                      self.download_tree, self.liked_tree, self.queue_tree]

        for tree in self.library_trees:
            tree.set_header_spacing(270, 270, 270)
            tree.tree.sortItems(0, 0)
        for tree in self.queue_trees:
            tree.set_header_spacing(270, 270, 270)
            tree.tree.sortItems(0, 0)
        for tree in self.search_trees:
            tree.set_header_spacing(65)
        self.songs_tree.set_header_spacing(65, -1, -1, -1, 65)
        self.albums_tree.set_header_spacing(65, -1, -1, 80)
        self.playlists_tree.set_header_spacing(65, -1, -1, 80)

    def _cover_art_loader(self, item):
        if item.img == "" and not item.id == "":
            item.img = get_cover_art(item.id)
            if type(item) == Track:
                item.update_meta_tags()
        self.request_cover_art(item.img)


class LoginDialog(QDialog, Ui_LoginDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.init_signals()
        set_label_image(self.bannerLabel, LOGO_BANNER)
        self.fail_index = 0
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.fail_strings = [
            "Incorrect username/password.",
            "Still incorrect username/password",
            "Think harder.",
            "This isn't gonna work out is it?"
        ]
        self.attempting_login = False

    def send_login(self):
        if self.attempting_login: return
        username = self.usernameInput.text()
        password = self.passwordInput.text()
        worker = Worker(ZSpotify.login, username, password)
        worker.signals.result.connect(self.login_result)
        self.attempting_login = True
        QThreadPool.globalInstance().start(worker)

    def login_result(self, success):
        self.attempting_login = False
        if success:
            self.accept()
        else:
            self.try_again_text()

    def try_again_text(self):
        self.loginInfoLabel.setText(self.fail_strings[self.fail_index])
        self.fail_index += 1
        if self.fail_index >= len(self.fail_strings): self.fail_index = 0

    def init_signals(self):
        self.loginBtn.clicked.connect(self.send_login)
        self.cancelBtn.clicked.connect(self.reject)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"CRITICAL ERROR: Main crashed. \nTraceback: \n{e}")
        logging.exception(f"CRITICAL ERROR: Main crashed. Error: {e}")
