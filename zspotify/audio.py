import os
import vlc
import time
import music_tag
from PyQt5 import QtCore, QtGui, QtTest
from PyQt5.QtCore import pyqtSignal, QThreadPool
from const import ROOT_PATH, SPOTIFY_ID, PLAY_ICON, PAUSE_ICON, TRACKTITLE, ARTIST, ALBUM, ARTWORK
from zspotify import ZSpotify
from worker import Worker
from item import Track


class MusicController:
    def __init__(self, window):
        self.window = window
        self.seeking = False
        self.worker = None
        self.audio_player = AudioPlayer(self.update_music_progress)
        self.init_signals()
        self.set_volume(self.window.volumeSlider.value())

    def play(self, item):
        if self.audio_player.play(item):
            self.set_icon(PAUSE_ICON)
            self.start_progress_worker()
        else:
            self.set_icon(PLAY_ICON)
            self.playing = False

    def start_progress_worker(self):
        if self.worker != None: return
        self.worker = Worker(self.run_progress_bar, 0, update=self.update_music_progress)
        self.worker.signals.finished.connect(self.on_progress_finished)
        QThreadPool.globalInstance().start(self.worker)


    def update_music_progress(self, perc):
        if not self.seeking:
            self.window.playbackBar.setValue(int(perc*10000))

    def run_progress_bar(self, signal, *args, **kwargs):
        time.sleep(1)
        while(self.audio_player.is_playing()):
            if self.audio_player.player.get_length() > 0:
                signal(self.audio_player.get_elapsed_percent())
            QtTest.QTest.qWait(100)

    def on_progress_finished(self):
        self.worker = None

    def on_seek(self):
        self.seeking = True

    def on_stop_seeking(self):
        percent = self.window.playbackBar.value()/self.window.playbackBar.maximum()
        self.audio_player.set_time(percent)
        self.seeking = False

    def set_volume(self, value):
        self.audio_player.set_volume(value)

    def on_press_play(self):
        if self.audio_player.is_playing():
            self.set_icon(PLAY_ICON)
            self.audio_player.pause()
        elif self.window.selected_item != None:
            if not self.audio_player.is_playing() and self.audio_player.player != None:
                self.audio_player.player.set_pause(1)
                self.set_icon(PAUSE_ICON)
                self.start_progress_worker()
            else:
                self.play(self.window.selected_item)
                self.set_icon(PLAY_ICON)


    def set_icon(self, icon_path):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.window.playBtn.setIcon(icon)
        self.window.playBtn.setIconSize(QtCore.QSize(24, 24))
        self.audio_player.pause()

    def init_signals(self):
        self.window.playBtn.clicked.connect(self.on_press_play)
        self.window.playbackBar.sliderPressed.connect(self.on_seek)
        self.window.playbackBar.sliderReleased.connect(self.on_stop_seeking)
        self.window.volumeSlider.valueChanged.connect(self.set_volume)


class AudioPlayer:

    SUPPORTED_FORMATS = ["mp3"]

    def __init__(self, update):
        self.player = None
        self.track = None
        self.audio_file = ""
        self.root = ZSpotify.get_config(ROOT_PATH)
        self.file_format = ".mp3"
        self.player = None
        self.playing = False
        self.prog_tick_rate = 100
        self.volume = 100

    def play(self, track):
        if self.player != None and self.track != None:
                if self.is_playing:
                    self.player.stop()

        abs_root = os.path.abspath(self.root)
        self.audio_file = find_local_track(track.id)
        if self.audio_file != None:
            self.track = track
            self.playing = True
            self.player = vlc.MediaPlayer(f"{self.root}/{self.audio_file}")
            self.set_volume(self.volume)
            self.player.play()
            return True
        return False

    def pause(self):
        self.player.pause()
        self.playing = False

    def unpause(self):
        self.player.play()

    def get_elapsed_percent(self):
        if self.player == None or self.player.get_length() == 0: return 0
        return self.player.get_time()/self.player.get_length()

    def set_time(self, percent):
        if self.player == None: return
        self.player.set_position(percent)


    def is_playing(self):
        if self.player != None and self.player.is_playing():
            self.playing = self.player.is_playing()
            return True
        return False

    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        if self.player != None:
            self.player.audio_set_volume(value)



def find_local_track(id):
    track_files = find_local_tracks()
    for file in track_files:
        if find_id_in_metadata(file) == str(id): return file
    return None

def find_local_tracks():
    root = ZSpotify.get_config(ROOT_PATH)
    dir = os.listdir(root)
    track_files = []
    for file in dir:
        split = file.split(".")
        if not len(split) >= 2 or split[1] not in AudioPlayer.SUPPORTED_FORMATS:
            continue
        else:
            track_files.append(file)
    return track_files

def get_track_file_as_item(file, index):
    split = file.split(".")
    if not len(split) >= 2 or split[1] not in AudioPlayer.SUPPORTED_FORMATS:
        return None
    download_directory = os.path.join(os.path.dirname(
        __file__), ZSpotify.get_config(ROOT_PATH))
    path = f"{download_directory}/{file}"
    tag = music_tag.load_file(path)
    track = Track(index, str(tag[SPOTIFY_ID]), str(tag[TRACKTITLE]), str(tag[ARTIST]), \
        album=str(tag[ALBUM]), downloaded=True)
    return track

def find_id_in_metadata(file_name):
    download_directory = os.path.join(os.path.dirname(
        __file__), ZSpotify.get_config(ROOT_PATH))
    file = f"{download_directory}/{file_name}"

    tag = music_tag.load_file(file)
    return str(tag[SPOTIFY_ID])
