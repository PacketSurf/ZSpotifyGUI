import os
import vlc
import time
import random
import music_tag
import logging
import struct
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtCore import pyqtSignal, QThreadPool, QObject
from PyQt5.QtGui import QImage, QPixmap
from const import COMMENT, ID, ARTWORK, PLAY_ICON, PAUSE_ICON, TRACKTITLE, ARTIST, ALBUM, ARTWORK, FORMATS, \
    VOL_ICON, MUTE_ICON, SHUFFLE_ON_ICON, SHUFFLE_OFF_ICON, REPEAT_ON_ICON, REPEAT_OFF_ICON, NEXT_ICON, PREV_ICON,\
    LISTEN_QUEUE_ICON
from zspotify import ZSpotify
from worker import Worker, MusicSignals
from item import Item, Track
from utils import ms_to_time_str, parse_meta_data
from glob import glob
from view import set_button_icon, set_label_image
from config import Config

logger = logging.getLogger(__name__)


class MusicController(QObject):

    onPlay = pyqtSignal(Item)

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.item = None
        self.playlist_tree = None
        self.shuffle = False
        self.repeat = False
        self.listen_queue = []
        self.shuffle_queue = []
        self.awaiting_play = False
        self.queue_next_song = False
        self.paused = False
        self.seeking = False
        self.worker = None
        self.audio_player = AudioPlayer(self.update_music_progress)
        self.init_signals()
        self.set_volume(self.window.volumeSlider.value())
        set_button_icon(self.window.playBtn, PLAY_ICON)
        set_button_icon(self.window.nextBtn, NEXT_ICON)
        set_button_icon(self.window.prevBtn, PREV_ICON)
        set_button_icon(self.window.shuffleBtn, SHUFFLE_OFF_ICON)
        set_button_icon(self.window.repeatBtn, REPEAT_OFF_ICON)
        set_button_icon(self.window.listenQueueBtn, LISTEN_QUEUE_ICON)


    def play(self, item, playlist_tree):
        if not playlist_tree.can_play: return
        if self.audio_player.play(item):
            logger.info(f"Playing track: {item.id}")
            self.start_progress_worker()
            self.queue_next_song = False
            self.paused = False
            self.update_playing_info(item)
            self.set_button_icon(self.window.playBtn, PAUSE_ICON)
            self.awaiting_play = True
            self.item = item
            if self.shuffle and self.playlist_tree != playlist_tree and playlist_tree.can_play:
                self.shuffle_queue = playlist_tree.items.copy()
                random.shuffle(self.shuffle_queue)
            if playlist_tree.can_play:
                self.playlist_tree = playlist_tree
                self.playlist_tree.select_item(item)
            self.onPlay.emit(item)


    def start_progress_worker(self):
        self.worker = Worker(self.run_progress_bar, update=self.update_music_progress, signals=MusicSignals())
        self.worker.signals.finished.connect(self.on_progress_finished)
        self.worker.signals.error.connect(lambda e: logging.error(e))
        QThreadPool.globalInstance().start(self.worker)

    def pause(self):
        self.set_button_icon(self.window.playBtn, PLAY_ICON)
        self.paused = True
        self.queue_next_song = False
        self.audio_player.pause()

    def unpause(self):
        self.set_button_icon(self.window.playBtn, PAUSE_ICON)
        self.paused = False
        self.queue_next_song = True
        self.audio_player.unpause()
        self.start_progress_worker()

    def queue_track(self, item, index=-1):
        if not item: return
        if index == -1:
            self.listen_queue.append(item)
        else:
             self.listen_queue.insert(index,item)

    def remove_track(self, item):
        if not item: return
        if item in self.shuffle_queue:
            self.shuffle_queue.remove(item)
        if item in self.listen_queue:
            self.listen_queue.remove(item)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.repeat: self.toggle_repeat()
        if self.shuffle:
            if self.playlist_tree and self.playlist_tree.items:
                self.set_button_icon(self.window.shuffleBtn, SHUFFLE_ON_ICON)
                self.shuffle_queue = self.playlist_tree.items.copy()
                random.shuffle(self.shuffle_queue)
        else:
            self.set_button_icon(self.window.shuffleBtn, SHUFFLE_OFF_ICON)

    def toggle_repeat(self):
        self.repeat = not self.repeat
        if self.repeat:
            self.set_button_icon(self.window.repeatBtn, REPEAT_ON_ICON)
        else:
            self.set_button_icon(self.window.repeatBtn, REPEAT_OFF_ICON)

    def update_music_progress(self, perc, elapsed, total):
        if not self.seeking:
            self.window.playbackBar.setValue(int(perc*100000000))
            self.queue_next_song = True
        if self.seeking:
            duration = self.audio_player.player.get_length()
            playback_bar_perc = self.window.playbackBar.value()/self.window.playbackBar.maximum()
            self.window.elapsedTimeLabel.setText(ms_to_time_str(duration * playback_bar_perc))
            self.window.remainingTimeLabel.setText(f"-{ms_to_time_str(duration * (1-playback_bar_perc))}")
        self.window.elapsedTimeLabel.setText(ms_to_time_str(elapsed))
        self.window.remainingTimeLabel.setText(f"-{ms_to_time_str(int(total)-int(elapsed))}")

    def run_progress_bar(self, signal, *args, **kwargs):
        while self.audio_player.is_playing() or self.awaiting_play:
            self.awaiting_play = False
            if self.audio_player and self.audio_player.player.get_length() > 0:
                signal(round(self.audio_player.get_elapsed_percent(), 9), self.audio_player.player.get_time(),
                       self.audio_player.player.get_length())
            QtTest.QTest.qWait(100)

    def on_progress_finished(self):
        self.worker = None
        if self.queue_next_song:
            self.on_next()

    def set_volume(self, value):
        self.audio_player.set_volume(value)
        if value == 0:
            set_label_image(self.window.volIconLabel, MUTE_ICON)
        else: set_label_image(self.window.volIconLabel, VOL_ICON)

    def on_press_play(self):
        if self.audio_player.is_playing():
            self.pause()
        elif self.window.selected_item:
            if not self.paused and self.window.selected_item and self.window.selected_tab:
                self.play(self.window.selected_item, self.window.selected_tab)
            else: self.unpause()

    def seek_to_percent(self, percent):
        self.seeking = True
        self.audio_player.set_time(percent)
        self.seeking = False

    def on_seek(self):
        self.seeking = True

    def on_stop_seeking(self):
        percent = self.window.playbackBar.value()/self.window.playbackBar.maximum()
        self.audio_player.set_time(percent)
        self.seeking = False

    def on_next(self):
        if not self.item and not self.playlist_tree: return
        if self.repeat:
            item = self.item
        elif len(self.listen_queue) > 0:
            item = self.listen_queue[0]
            self.listen_queue.pop(0)
        elif self.shuffle:
            if self.item not in self.shuffle_queue and self.playlist_tree.can_shuffle:
                self.shuffle_queue = self.playlist_tree.items.copy()
                random.shuffle(self.shuffle_queue)
            index = self.shuffle_queue.index(self.item)
            index += 1
            if index >= len(self.shuffle_queue):
                random.shuffle(self.shuffle_queue)
                index = 0
            item = self.shuffle_queue[index]
        else:
            item = self.window.select_next_item(self.item, self.playlist_tree)
        if item: self.play(item, self.playlist_tree)

    def on_prev(self):
        if not self.item and not self.playlist_tree: return
        if self.audio_player.is_playing():
            if self.audio_player.player and self.audio_player.player.get_time() > 15000:
                self.awaiting_play = True
                self.audio_player.restart()
                return
        if self.shuffle and self.item in self.shuffle_queue:
            index = self.shuffle_queue.index(self.item)
            index -= 1
            if index < 0:
                return
            item = self.shuffle_queue[index]
        else:
            item = self.window.select_prev_item(self.item, self.playlist_tree)
        if item: self.play(item, self.playlist_tree)

    def on_play_queue_song(self):
        if not self.window.selected_item: return
        item = self.window.selected_item
        if item in self.shuffle_queue:
            self.shuffle_queue


    def update_playing_info(self, item):
        self.window.playingInfo1.setText(item.title)
        self.window.playingInfo1.setToolTip(item.title)
        self.window.playingInfo2.setText(item.artists)
        self.window.playingInfo2.setToolTip(item.artists)

    def set_button_icon(self, btn, icon_path):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        btn.setIcon(icon)

    def set_vol_icon(self, icon_path):
        lbl = self.window.volIconLabel
        pixmap = QPixmap(icon_path)
        lbl.setPixmap(pixmap)
        lbl.setScaledContents(True)
        lbl.show()

    def init_signals(self):
        self.window.playBtn.clicked.connect(self.on_press_play)
        self.window.playbackBar.sliderPressed.connect(self.on_seek)
        self.window.playbackBar.sliderReleased.connect(self.on_stop_seeking)
        self.window.playbackBar.onClicked.connect(self.on_seek)
        self.window.playbackBar.onReleased.connect(self.seek_to_percent)
        self.window.volumeSlider.valueChanged.connect(self.set_volume)
        self.window.nextBtn.clicked.connect(self.on_next)
        self.window.prevBtn.clicked.connect(self.on_prev)
        self.window.shuffleBtn.clicked.connect(self.toggle_shuffle)
        self.window.repeatBtn.clicked.connect(self.toggle_repeat)


class AudioPlayer:

    def __init__(self, update):
        self.player = None
        self.track = None
        self.audio_file = ""
        self.root = Config.get_root_path()
        self.file_format = ".mp3"
        self.player = None
        self.playing = False
        self.prog_tick_rate = 100
        self.volume = 100

    def play(self, track):
        if self.player and self.track and self.is_playing:
            self.player.stop()
        self.audio_file = track.path
        if self.audio_file:
            self.track = track
            self.playing = True
            try:
                self.player = vlc.MediaPlayer(f"{self.audio_file}")
                self.set_volume(self.volume)
                self.player.play()
            except Exception as e:
                logger.error(e)
            return True
        return False

    def pause(self):
        self.player.pause()
        self.playing = False

    def unpause(self):
        self.player.play()

    def restart(self):
        if self.player:
            self.player.set_time(0)

    def get_elapsed_percent(self):
        if not self.player or self.player.get_length() == 0:
            return 0
        return self.player.get_time()/self.player.get_length()

    def set_time(self, percent):
        if not self.player: return
        self.player.set_position(percent)

    def is_playing(self):
        if self.player and self.player.is_playing():
            self.playing = self.player.is_playing()
            return True
        return False

    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        if self.player:
            self.player.audio_set_volume(value)


def find_local_track(id):
    track_files = find_local_tracks()
    for file in track_files:
        if find_id_in_metadata(file) == str(id): return file
    return None


def find_local_tracks():
    root = Config.get_root_path()
    all_results = []
    for format in FORMATS:
        try:
            ext = "*." + format
            results = [y for x in os.walk(root) for y in glob(os.path.join(x[0], ext))]
            all_results += results
        except Exception as e:
            logger.error(e)
    return all_results


def get_track_file_as_item(file, index):
    for format in FORMATS:
        if format in file:
            tag = music_tag.load_file(file)
            meta_data = parse_meta_data(tag[COMMENT])
            item_id = meta_data.get(ID) or ""
            img = meta_data.get(ARTWORK) or ""
            track = Track(index, item_id, str(tag[TRACKTITLE]), str(tag[ARTIST]),
                          album=str(tag[ALBUM]), img=img, downloaded=True, path=Path(file))
            return track
    return None


def find_id_in_metadata(path):
    tag = music_tag.load_file(path)
    data = parse_meta_data(tag[COMMENT])
    return data.get(ID) if None else ""
