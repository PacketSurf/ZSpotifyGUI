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

CONFIG_VALUES = {
    ROOT_PATH:                  { 'default': '../ZSpotify Music/',    'type': 'str',  'arg': '--root-path'                  },
    ROOT_PODCAST_PATH:          { 'default': '../ZSpotify Podcasts/', 'type': 'str',  'arg': '--root-podcast-path'          },
    SKIP_EXISTING_FILES:        { 'default': True,                    'type': 'bool', 'arg': '--skip-existing-files'        },
    SKIP_PREVIOUSLY_DOWNLOADED: { 'default': False,                   'type': 'bool', 'arg': '--skip-previously-downloaded' },
    DOWNLOAD_FORMAT:            { 'default': 'ogg',                   'type': 'str',  'arg': '--download-format'            },
    FORCE_PREMIUM:              { 'default': False,                   'type': 'bool', 'arg': '--force-premium'              },
    ANTI_BAN_WAIT_TIME:         { 'default': 1,                       'type': 'int',  'arg': '--anti-ban-wait-time'         },
    OVERRIDE_AUTO_WAIT:         { 'default': False,                   'type': 'bool', 'arg': '--override-auto-wait'         },
    CHUNK_SIZE:                 { 'default': 50000,                   'type': 'int',  'arg': '--chunk-size'                 },
    SPLIT_ALBUM_DISCS:          { 'default': False,                   'type': 'bool', 'arg': '--split-album-discs'          },
    DOWNLOAD_REAL_TIME:         { 'default': False,                   'type': 'bool', 'arg': '--download-real-time'         },
    LANGUAGE:                   { 'default': 'en',                    'type': 'str',  'arg': '--language'                   },
    BITRATE:                    { 'default': '',                      'type': 'str',  'arg': '--bitrate'                    },
}


class Config:
    Values = {}

    @classmethod
    def load(cls, args) -> None:
        app_dir = os.path.dirname(__file__)

        config_fp = CONFIG_FILE_PATH
        if args.config_location:
            config_fp = args.config_location

        true_config_file_path = os.path.join(app_dir, config_fp)

        if not os.path.exists(true_config_file_path):
            with open(true_config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(cls.get_default_json(), config_file, indent=4)
            cls.Values = cls.get_default_json()
        else:
            with open(true_config_file_path, encoding='utf-8') as config_file:
                cls.Values = json.load(config_file)
        for key in CONFIG_VALUES:
            if key not in cls.Values:
                cls.Values[key] = CONFIG_VALUES[key].default

    @classmethod
    def get_default_json(cls) -> Any:
        r = {}
        for key in CONFIG_VALUES:
            r[key] = CONFIG_VALUES[key].default
        return r

    @classmethod
    def get(cls, key) -> Any:
        return cls.Values.get(key)

    @classmethod
    def get_root_path(cls) -> str:
        return cls.get(ROOT_PATH)

    @classmethod
    def get_root_podcast_path(cls) -> str:
        return cls.get(ROOT_PODCAST_PATH)

    @classmethod
    def get_skip_existing_files(cls) -> bool:
        return cls.get(SKIP_EXISTING_FILES)

    @classmethod
    def get_skip_previously_downloaded(cls) -> bool:
        return cls.get(SKIP_PREVIOUSLY_DOWNLOADED)

    @classmethod
    def get_split_album_discs(cls) -> bool:
        return cls.get(SPLIT_ALBUM_DISCS)

    @classmethod
    def get_chunk_size(cls) -> int():
        return cls.get(CHUNK_SIZE)

    @classmethod
    def get_override_auto_wait(cls) -> bool:
        return cls.get(OVERRIDE_AUTO_WAIT)

    @classmethod
    def get_force_premium(cls) -> bool:
        return cls.get(FORCE_PREMIUM)

    @classmethod
    def get_download_format(cls) -> str:
        return cls.get(DOWNLOAD_FORMAT)

    @classmethod
    def get_anti_ban_wait_time(cls) -> int:
        return cls.get(ANTI_BAN_WAIT_TIME)

    @classmethod
    def get_language(cls) -> str:
        return cls.get(LANGUAGE)

    @classmethod
    def get_download_real_time(cls) -> bool:
        return cls.get(DOWNLOAD_REAL_TIME)

    @classmethod
    def get_bitrate(cls) -> str:
        return cls.get(BITRATE)
