import os
import vlc
import time
import music_tag
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QThreadPool
from const import ROOT_PATH, SPOTIFY_ID
from zspotify import ZSpotify
from worker import Worker


class AudioPlayer:

    def __init__(self, update):
        self.track = None
        self.audio_file = ""
        self.root = ZSpotify.get_config(ROOT_PATH)
        self.file_format = ".mp3"
        self.supported_formats = ["mp3"]
        self.player = None
        self.playing = False
        self.update = update
        self.prog_tick_rate = 100

    def play(self, track):
        if self.player != None and self.track != None:
            if self.track.id != track.id:
                self.player.pause()
                self.playing = False
            else:
                if self.playing:
                    self.player.pause()
                    self.playing = False
                    return
                else:
                    self.player.play()
                    self.playing = True
                    return

        abs_root = os.path.abspath(self.root)
        self.audio_file = self.find_local_track(track.id)
        if self.audio_file != None:
            self.track = track
            self.playing = True
            self.player = vlc.MediaPlayer(f"{self.root}/{self.audio_file}")
            self.player.play()

    def get_elapsed_percent(self):
        if self.player.get_length() == 0: return 0
        return self.player.get_time()/self.player.get_length()



    def set_time(self, percent):
        self.player.set_position(percent)

    def find_local_track(self, id):
        dir = os.listdir(self.root)
        for file in dir:
            split = file.split(".")
            if not len(split) >= 2 or split[1] not in self.supported_formats: continue
            download_directory = os.path.join(os.path.dirname(
                __file__), ZSpotify.get_config(ROOT_PATH))
            filename = f"{download_directory}/{file}"
            tag = music_tag.load_file(filename)
            if str(tag[SPOTIFY_ID]) == str(id): return file
        return None


#path = "../ZSpotify Music/"
#song = "Kwengface - Petrol Station.mp3"
#p = vlc.MediaPlayer(f"{path}{song}")
#p.play()
#while not p.will_play():
#    time.sleep(0.1)

#time.sleep(p.get_length())
