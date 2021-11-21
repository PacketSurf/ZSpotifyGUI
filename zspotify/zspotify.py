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

from const import TYPE, \
    PREMIUM, USER_READ_EMAIL, AUTHORIZATION, OFFSET, LIMIT, \
    PLAYLIST_READ_PRIVATE, USER_LIBRARY_READ
from config import Config


class ZSpotify:
    SESSION: Session = None
    DOWNLOAD_QUALITY = None
    CONFIG: Config = Config()

    def __init__(self, args):
        ZSpotify.CONFIG.load(args)
        ZSpotify.login()

    @classmethod
    def login(cls):
        """ Authenticates with Spotify and saves credentials to a file """

        cred_location = os.path.join(os.getcwd(), Config.get_credentials_location())

        if os.path.isfile(cred_location):
            try:
                cls.SESSION = Session.Builder().stored_file(cred_location).create()
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
    def get_content_stream(cls, content_id, quality):
        return cls.SESSION.content_feeder().load(content_id, VorbisOnlyAudioQuality(quality), False, None)

    @classmethod
    def __get_auth_token(cls):
        return cls.SESSION.tokens().get_token(USER_READ_EMAIL, PLAYLIST_READ_PRIVATE, USER_LIBRARY_READ).access_token

    @classmethod
    def get_auth_header(cls):
        return {
            'Authorization': f'Bearer {cls.__get_auth_token()}',
            'Accept-Language': f'{cls.CONFIG.get_language()}'
        }

    @classmethod
    def get_auth_header_and_params(cls, limit, offset):
        return {
            'Authorization': f'Bearer {cls.__get_auth_token()}',
            'Accept-Language': f'{cls.CONFIG.get_language()}'
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
        return (cls.SESSION.get_user_attribute(TYPE) == PREMIUM) or cls.CONFIG.get_force_premium()
