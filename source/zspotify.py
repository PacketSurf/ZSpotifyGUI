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
import logging
import requests
from librespot.audio.decoders import VorbisOnlyAudioQuality, AudioQuality
from librespot.core import Session

from const import TYPE, ITEMS, \
    USER_READ_EMAIL, AUTHORIZATION, OFFSET, LIMIT, PREMIUM,\
    PLAYLIST_READ_PRIVATE,TRACK, NAME, ID, ARTIST, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUM, ALBUMS, \
    OWNER, PLAYLIST, PLAYLISTS, DISPLAY_NAME, IMAGES, URL, TOTAL_TRACKS, TOTAL, RELEASE_DATE, USER_LIBRARY_READ, DURATION
from utils import MusicFormat, ms_to_time_str
from item import Track, Album, Artist, Playlist
from config import Config

logger = logging.getLogger(__name__)

class ZSpotify:
    SESSION: Session = None
    DOWNLOAD_QUALITY = None
    IS_PREMIUM = False
    SEARCH_URL = 'https://api.spotify.com/v1/search'


    @classmethod
    def login(cls, username="", password=""):
        """ Authenticates with Spotify and saves credentials to a file """

        cred_location = Config.get_credentials_location()

        if os.path.isfile(cred_location):
            try:
                cls.SESSION = Session.Builder().stored_file().create()
            except:
                logger.info("No credentials file found. New login details required.")
                return False
        elif username != "" and password != "":
            try:
                conf = Session.Configuration.Builder().set_stored_credential_file(cred_location).build()
                cls.SESSION = Session.Builder(conf).user_pass(username, password).create()
            except Exception as e:
                logger.error(e)
                return False
        else: return
        if ZSpotify.check_premium():
            ZSpotify.DOWNLOAD_QUALITY = AudioQuality.VERY_HIGH
        else:
            ZSpotify.DOWNLOAD_QUALITY = AudioQuality.HIGH
        return True

    @classmethod
    def logout(cls):
        if cls.SESSION:
            cls.SESSION.close()

    @classmethod
    def search(cls, search_terms):
        # Clean search term
        """ Searches Spotify's API for relevant data """
        results = Config.get_total_search_results()
        params = {'limit': results,
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
                try:
                    artists = ', '.join([artist[NAME] for artist in t[ARTISTS]])
                    url = t[ALBUM][IMAGES][1][URL]
                    duration = ms_to_time_str(t[DURATION])
                    track = Track(counter, t[ID], str(t[NAME]), artists, str(t[ALBUM][NAME]), \
                        release_date=t[ALBUM][RELEASE_DATE], duration=duration, img=url)
                    results[TRACKS].append(track)
                    counter += 1
                except Exception as e:
                    logger.error(e)
        counter = 1
        if resp[ALBUMS] != None:
            for a in resp[ALBUMS][ITEMS]:
                try:
                    if len(a[IMAGES]) > 1:
                        url = a[IMAGES][1][URL]
                    else:
                        url = ""
                    artists = ', '.join([artist[NAME] for artist in a[ARTISTS]])
                    album = Album(counter, a[ID], a[NAME], artists, a[TOTAL_TRACKS], release_date=a[RELEASE_DATE], img=url)
                    results[ALBUMS].append(album)
                    counter += 1
                except Exception as e:
                    logger.error(e)
        counter = 1
        if resp[ARTISTS] != None:
            for ar in resp[ARTISTS][ITEMS]:
                try:
                    if len(ar[IMAGES]) >= 1:
                        url = ar[IMAGES][1][URL]
                    else: url = ""
                    artist = Artist(counter, ar[ID], ar[NAME], img=url)
                    results[ARTISTS].append(artist)
                    counter += 1
                except Exception as e:
                    logger.error(e)
        counter = 1
        if resp[ARTISTS] != None:
            for playlist in resp[PLAYLISTS][ITEMS]:
                try:
                    if len(playlist[IMAGES]) > 0:
                        url = playlist[IMAGES][0][URL]
                    else:
                        url = ""
                    playlist = Playlist(counter, playlist[ID], playlist[NAME], playlist[OWNER][DISPLAY_NAME], playlist[TRACKS][TOTAL], img=url)
                    results[PLAYLISTS].append(playlist)
                    counter += 1
                except Exception as e:
                    logger.error(e)
        return results

    @classmethod
    def load_tracks_url(cls, url):
        text, items = cls.invoke_url(url)
        if not items or len(items) <= 0: return
        index = 0
        tracks = []
        for item in items[ITEMS]:
            artists = ', '.join([artist[NAME] for artist in item[TRACK][ARTISTS]])
            duration = ms_to_time_str(item[TRACK][DURATION])
            track = Track(index, item[TRACK][ID], item[TRACK][NAME], artists, album=item[TRACK][ALBUM][NAME], \
            img=item[TRACK][ALBUM][IMAGES][1][URL], duration=duration)
            tracks.append(track)
        return tracks

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
            'Accept-Language': f'{Config.get_language()}'
        }

    @classmethod
    def get_auth_header_and_params(cls, limit, offset):
        return {
            'Authorization': f'Bearer {cls.__get_auth_token()}',
            'Accept-Language': f'{Config.get_language()}'
        }, {LIMIT: limit, OFFSET: offset}

    @classmethod
    def send_url(cls, url):
        headers = cls.get_auth_header()
        return requests.put(url, headers=headers)

    @classmethod
    def invoke_url_with_params(cls, url, limit, offset, **kwargs):
        headers, params = cls.get_auth_header_and_params(limit=limit, offset=offset)
        params.update(kwargs)
        return requests.get(url, headers=headers, params=params).json()

    @classmethod
    def invoke_url(cls, url):
        headers = cls.get_auth_header()
        response = requests.get(url, headers=headers)
        return response.text, response.json()

    @classmethod
    def check_premium(cls) -> bool:
        """ If user has spotify premium return true """
        cls.IS_PREMIUM = (cls.SESSION.get_user_attribute(TYPE) == PREMIUM) or Config.get_force_premium()
        return cls.IS_PREMIUM
