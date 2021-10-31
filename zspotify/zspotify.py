#! /usr/bin/env python3

"""
ZSpotify
It's like youtube-dl, but for Spotify.

(Made by Deathmonger/Footsiefat - @doomslayer117:matrix.org)
"""
import json
import os
import os.path
from typing import Any

import requests
from librespot.audio.decoders import VorbisOnlyAudioQuality, AudioQuality
from librespot.core import Session

from const import CREDENTIALS_JSON, TYPE, \
    PREMIUM, USER_READ_EMAIL, AUTHORIZATION, OFFSET, LIMIT, CONFIG_FILE_PATH, FORCE_PREMIUM, \
    PLAYLIST_READ_PRIVATE, CONFIG_DEFAULT_SETTINGS,TRACK, NAME, ID, ARTIST, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUM, ALBUMS, \
    OWNER, PLAYLIST, PLAYLISTS, DISPLAY_NAME, IMAGES, URL, TOTAL_TRACKS, TOTAL, RELEASE_DATE, USER_LIBRARY_READ
from utils import MusicFormat
from search_data import Track, Album, Artist, Playlist



class ZSpotify:
    SESSION: Session = None
    DOWNLOAD_QUALITY = None
    IS_PREMIUM = False
    CONFIG = {}
    SEARCH_URL = 'https://api.spotify.com/v1/search'


    @classmethod
    def login(cls, username="", password=""):
        """ Authenticates with Spotify and saves credentials to a file """

        if os.path.isfile(CREDENTIALS_JSON):
            try:
                cls.SESSION = Session.Builder().stored_file().create()
            except:
                return False
        elif username != "" and password != "":
            try:
                cls.SESSION = Session.Builder().user_pass(username, password).create();
            except Exception as e:
                print(e)
                return False
        else: return
        if ZSpotify.check_premium():
            ZSpotify.DOWNLOAD_QUALITY = AudioQuality.VERY_HIGH
        else:
            ZSpotify.DOWNLOAD_QUALITY = AudioQuality.HIGH
        return True


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
    def search(cls, search_terms):
        # Clean search term
        """ Searches Spotify's API for relevant data """
        params = {'limit': '50',
                  'offset': '0',
                  'q': search_terms,
                  'type': 'track,album,artist,playlist'}

        splits = search_terms.split()
        search_term_list = []
        for split in splits:
            if split[0] == "-":
                break
            search_term_list.append(split)
        if not search_term_list:
            raise ValueError("Invalid query.")
        search_term = ' '.join(search_term_list)

        resp = cls.invoke_url_with_params(cls.SEARCH_URL, **params)

        dics = []
        results = {TRACKS:[], ARTISTS:[],ALBUMS:[], PLAYLISTS:[]}
        counter = 1
        if resp[TRACKS] != None:
            for t in resp[TRACKS][ITEMS]:
                artists = ' & '.join([artist[NAME] for artist in t[ARTISTS]])
                url = t[ALBUM][IMAGES][1][URL]
                track = Track(counter, t[ID], str(t[NAME]), artists, str(t[ALBUM][NAME]), release_date=t[ALBUM][RELEASE_DATE],img=url)
                results[TRACKS].append(track)
                counter += 1
        counter = 1
        if resp[ALBUMS] != None:
            for a in resp[ALBUMS][ITEMS]:
                if len(a[IMAGES]) > 1:
                    url = a[IMAGES][1][URL]
                else:
                    url = ""
                artists = ' & '.join([artist[NAME] for artist in a[ARTISTS]])
                album = Album(counter, a[ID], a[NAME], artists, a[TOTAL_TRACKS], release_date=a[RELEASE_DATE], img=url)
                results[ALBUMS].append(album)
                counter += 1
        counter = 1
        if resp[ARTISTS] != None:
            for ar in resp[ARTISTS][ITEMS]:
                if len(ar[IMAGES]) >= 1:
                    url = ar[IMAGES][1][URL]
                else: url = ""
                artist = Artist(counter, ar[ID], ar[NAME], img=url)
                results[ARTISTS].append(artist)
                counter += 1
        counter = 1
        if resp[ARTISTS] != None:
            for playlist in resp[PLAYLISTS][ITEMS]:
                if len(playlist[IMAGES]) > 0:
                    url = playlist[IMAGES][0][URL]
                else:
                    url = ""
                playlist = Playlist(counter, playlist[ID], playlist[NAME], playlist[OWNER][DISPLAY_NAME], playlist[TRACKS][TOTAL], img=url)
                results[PLAYLISTS].append(playlist)
                counter += 1

        return results

    @classmethod
    def set_config(cls, key, value):
        cls.CONFIG[key] = value
        app_dir = os.path.dirname(__file__)
        true_config_file_path = os.path.join(app_dir, CONFIG_FILE_PATH)
        with open(true_config_file_path, 'w', encoding='utf-8') as config_file:
            json.dump(cls.CONFIG, config_file, indent=4)

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
            AUTHORIZATION: f'Bearer {cls.__get_auth_token()}'}

    @classmethod
    def get_auth_header_and_params(cls, limit, offset):
        return {AUTHORIZATION: f'Bearer {cls.__get_auth_token()}'}, {LIMIT: limit, OFFSET: offset}

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
        cls.IS_PREMIUM = (cls.SESSION.get_user_attribute(TYPE) == PREMIUM) or cls.get_config(FORCE_PREMIUM)
        return cls.IS_PREMIUM
