import json
import os
import sys
from typing import Any

CONFIG_FILE_PATH = '../zs_config.json'

ROOT_PATH = 'ROOT_PATH'
ROOT_PODCAST_PATH = 'ROOT_PODCAST_PATH'
SKIP_EXISTING_FILES = 'SKIP_EXISTING_FILES'
SKIP_PREVIOUSLY_DOWNLOADED = 'SKIP_PREVIOUSLY_DOWNLOADED'
DOWNLOAD_FORMAT = 'DOWNLOAD_FORMAT'
FORCE_PREMIUM = 'FORCE_PREMIUM'
ANTI_BAN_WAIT_TIME = 'ANTI_BAN_WAIT_TIME'
OVERRIDE_AUTO_WAIT = 'OVERRIDE_AUTO_WAIT'
CHUNK_SIZE = 'CHUNK_SIZE'
SPLIT_ALBUM_DISCS = 'SPLIT_ALBUM_DISCS'
DOWNLOAD_REAL_TIME = 'DOWNLOAD_REAL_TIME'
LANGUAGE = 'LANGUAGE'
BITRATE = 'BITRATE'

CONFIG_DEFAULT_SETTINGS = {
    'ROOT_PATH': '../ZSpotify Music/',
    'ROOT_PODCAST_PATH': '../ZSpotify Podcasts/',
    'SKIP_EXISTING_FILES': True,
    'SKIP_PREVIOUSLY_DOWNLOADED': False,
    'DOWNLOAD_FORMAT': 'ogg',
    'FORCE_PREMIUM': False,
    'ANTI_BAN_WAIT_TIME': 1,
    'OVERRIDE_AUTO_WAIT': False,
    'CHUNK_SIZE': 50000,
    'SPLIT_ALBUM_DISCS': False,
    'DOWNLOAD_REAL_TIME': False,
    'LANGUAGE': 'en',
    'BITRATE': '',
}

class Config:

    Values = {}

    @classmethod
    def load(cls, args) -> None:
        app_dir = os.path.dirname(__file__)
        true_config_file_path = os.path.join(app_dir, CONFIG_FILE_PATH)

        if not os.path.exists(true_config_file_path):
            with open(true_config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(CONFIG_DEFAULT_SETTINGS, config_file, indent=4)
            cls.Values = CONFIG_DEFAULT_SETTINGS
        else:
            with open(true_config_file_path, encoding='utf-8') as config_file:
                cls.Values = json.load(config_file)

    @classmethod
    def get(cls, key) -> Any:
        return cls.Values.get(key)
    
    @classmethod
    def getRootPath(cls) -> str:
        return cls.get(ROOT_PATH)

    @classmethod
    def getRootPodcastPath(cls) -> str:
        return cls.get(ROOT_PODCAST_PATH)

    @classmethod
    def getSkipExistingFiles(cls) -> bool:
        return cls.get(SKIP_EXISTING_FILES)

    @classmethod
    def getSkipPreviouslyDownloaded(cls) -> bool:
        return cls.get(SKIP_PREVIOUSLY_DOWNLOADED)

    @classmethod
    def getSplitAlbumDiscs(cls) -> bool:
        return cls.get(SPLIT_ALBUM_DISCS)

    @classmethod
    def getChunkSize(cls) -> int():
        return cls.get(CHUNK_SIZE)

    @classmethod
    def getOverrideAutoWait(cls) -> bool:
        return cls.get(OVERRIDE_AUTO_WAIT)

    @classmethod
    def getForcePremium(cls) -> bool:
        return cls.get(FORCE_PREMIUM)
    
    @classmethod
    def getDownloadFormat(cls) -> str:
        return cls.get(DOWNLOAD_FORMAT)
    
    @classmethod
    def getAntiBanWaitTime(cls) -> int:
        return cls.get(ANTI_BAN_WAIT_TIME)
    
    @classmethod
    def getLanguage(cls) -> str:
        return cls.get(LANGUAGE)

    @classmethod
    def getDownloadRealTime(cls) -> bool:
        return cls.get(DOWNLOAD_REAL_TIME)
    
    @classmethod
    def getBitrate(cls) -> str:
        return cls.get(BITRATE)
    