#! /usr/bin/env python3

"""
ZSpotify
It's like youtube-dl, but for Spotify.

(Made by Deathmonger/Footsiefat - @doomslayer117:matrix.org)
"""
import json
import os
import os.path
from getpass import getpass
from typing import Any

import requests
from librespot.audio.decoders import VorbisOnlyAudioQuality
from librespot.core import Session

from const import CREDENTIALS_JSON, TYPE, \
    PREMIUM, USER_READ_EMAIL, AUTHORIZATION, OFFSET, LIMIT, CONFIG_FILE_PATH, FORCE_PREMIUM, \
    PLAYLIST_READ_PRIVATE, USER_LIBRARY_READ, CONFIG_DEFAULT_SETTINGS
from utils import MusicFormat


class ZSpotify:
    SESSION: Session = None
    DOWNLOAD_QUALITY = None
    CONFIG = {}

    def __init__(self):
        ZSpotify.load_config()
        ZSpotify.login()

    @classmethod
    def login(cls):
        """ Authenticates with Spotify and saves credentials to a file """

        if os.path.isfile(CREDENTIALS_JSON):
            try:
                cls.SESSION = Session.Builder().stored_file().create()
                return
            except RuntimeError:
                pass
        while True:
            user_name = ''
            while len(user_name) == 0:
                user_name = input('Username: ')
            password = getpass()
            try:
                cls.SESSION = Session.Builder().user_pass(user_name, password).create()
                return
            except RuntimeError:
                pass

    @classmethod
    def load_config(cls) -> None:
        app_dir = os.path.dirname(__file__)
        true_config_file_path = os.path.join(app_dir, CONFIG_FILE_PATH)
        if not os.path.exists(true_config_file_path):
            with open(true_config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(CONFIG_DEFAULT_SETTINGS, config_file, indent=4)
            cls.CONFIG = CONFIG_DEFAULT_SETTINGS
        else:
            with open(true_config_file_path, encoding='utf-8') as config_file:
                cls.CONFIG = json.load(config_file)

    @classmethod
    def get_config(cls, key) -> Any:
        return cls.CONFIG.get(key)

    @classmethod
    def get_content_stream(cls, content_id, quality):
        return cls.SESSION.content_feeder().load(content_id, VorbisOnlyAudioQuality(quality), False, None)

    @classmethod
    def __get_auth_token(cls):
        return cls.SESSION.tokens().get_token(USER_READ_EMAIL, PLAYLIST_READ_PRIVATE, USER_LIBRARY_READ).access_token

    @classmethod
    def get_auth_header(cls):
        return {
            'Authorization': f'Bearer {cls.__get_auth_token()}',
            'Accept-Language': f'{cls.CONFIG.get("LANGUAGE")}'
        }

    @classmethod
    def get_auth_header_and_params(cls, limit, offset):
        return {
            'Authorization': f'Bearer {cls.__get_auth_token()}',
            'Accept-Language': f'{cls.CONFIG.get("LANGUAGE")}'
        }, {LIMIT: limit, OFFSET: offset}

    @classmethod
    def invoke_url_with_params(cls, url, limit, offset, **kwargs):
        headers, params = cls.get_auth_header_and_params(limit=limit, offset=offset)
        params.update(kwargs)
        return requests.get(url, headers=headers, params=params).json()

    @classmethod
    def invoke_url(cls, url):
        headers = cls.get_auth_header()
        return requests.get(url, headers=headers).json()

    @classmethod
    def check_premium(cls) -> bool:
        """ If user has spotify premium return true """
        return (cls.SESSION.get_user_attribute(TYPE) == PREMIUM) or cls.get_config(FORCE_PREMIUM)
