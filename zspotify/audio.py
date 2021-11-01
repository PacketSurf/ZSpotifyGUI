import os
import vlc
import time
import music_tag
from const import ROOT_PATH, COMMENT
from zspotify import ZSpotify

class AudioPlayer:
    def __init__(self):
        self.track = None
        self.audio_file = ""
        self.root = ZSpotify.get_config(ROOT_PATH)
        self.file_format = ".mp3"
        self.supported_formats = ["mp3"]
        self.player = None

    def play(self, track):
        if self.player != None:
            if self.player.is_playing():
                self.player.pause()
            else:
                self.player.play()
        else:
            abs_root = os.path.abspath(self.root)
            self.audio_file = self.find_local_track(id)
            if self.audio_file != None:
                self.player = vlc.MediaPlayer(f"{self.root}/{self.audio_file}")
                self.player.play()
            else:
                pass


    def find_local_track(self, id):
        dir = os.listdir(self.root)
        for file in dir:
            split = file.split(".")
            if not len(split) >= 2 or split[1] not in self.supported_formats: continue
            download_directory = os.path.join(os.path.dirname(
                __file__), ZSpotify.get_config(ROOT_PATH))
            filename = f"{download_directory}/{file}"
            tag = music_tag.load_file(filename)
            #if str(tag[COMMENT]) == str(id): return file
        return None


#path = "../ZSpotify Music/"
#song = "Kwengface - Petrol Station.mp3"
#p = vlc.MediaPlayer(f"{path}{song}")
#p.play()
#while not p.will_play():
#    time.sleep(0.1)

#time.sleep(p.get_length())
