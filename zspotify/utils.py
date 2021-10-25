import os
import platform
import re
import time
from enum import Enum
from typing import List, Tuple, Match

import music_tag
import requests

from const import SANITIZE, ARTIST, TRACKTITLE, ALBUM, YEAR, DISCNUMBER, TRACKNUMBER, ARTWORK, \
    WINDOWS_SYSTEM, TRACK_ID, ALBUM_ID, PLAYLIST_ID, EPISODE_ID, SHOW_ID, ARTIST_ID


class MusicFormat(str, Enum):
    MP3 = 'mp3',
    OGG = 'ogg',


def create_download_directory(download_path: str) -> None:
    os.makedirs(download_path, exist_ok=True)


def wait(seconds: int = 3) -> None:
    """ Pause for a set number of seconds """
    for second in range(seconds)[::-1]:
        print(f'\rWait for {second + 1} second(s)...', end='')
        time.sleep(1)


def split_input(selection) -> List[str]:
    """ Returns a list of inputted strings """
    inputs = []
    if '-' in selection:
        for number in range(int(selection.split('-')[0]), int(selection.split('-')[1]) + 1):
            inputs.append(number)
    else:
        selections = selection.split(',')
        for i in selections:
            inputs.append(i.strip())
    return inputs


def splash() -> None:
    """ Displays splash screen """
    print("""
███████ ███████ ██████   ██████  ████████ ██ ███████ ██    ██
   ███  ██      ██   ██ ██    ██    ██    ██ ██       ██  ██
  ███   ███████ ██████  ██    ██    ██    ██ █████     ████
 ███         ██ ██      ██    ██    ██    ██ ██         ██
███████ ███████ ██       ██████     ██    ██ ██         ██
    """)


def clear() -> None:
    """ Clear the console window """
    if platform.system() == WINDOWS_SYSTEM:
        os.system('cls')
    else:
        os.system('clear')


def sanitize_data(value) -> str:
    """ Returns given string with problematic removed """
    for pattern in SANITIZE:
        value = value.replace(pattern, '')
    return value.replace('|', '-')


def set_audio_tags(filename, artists, name, album_name, release_year, disc_number, track_number) -> None:
    """ sets music_tag metadata """
    tags = music_tag.load_file(filename)
    tags[ARTIST] = conv_artist_format(artists)
    tags[TRACKTITLE] = name
    tags[ALBUM] = album_name
    tags[YEAR] = release_year
    tags[DISCNUMBER] = disc_number
    tags[TRACKNUMBER] = track_number
    tags.save()


def conv_artist_format(artists) -> str:
    """ Returns converted artist format """
    return ', '.join(artists)


def set_music_thumbnail(filename, image_url) -> None:
    """ Downloads cover artwork """
    img = requests.get(image_url).content
    tags = music_tag.load_file(filename)
    tags[ARTWORK] = img
    tags.save()


def regex_input_for_urls(search_input) -> Tuple[str, str, str, str, str, str]:
    """ Since many kinds of search may be passed at the command line, process them all here. """
    track_uri_search = re.search(
        r'^spotify:track:(?P<TrackID>[0-9a-zA-Z]{22})$', search_input)
    track_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/track/(?P<TrackID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    album_uri_search = re.search(
        r'^spotify:album:(?P<AlbumID>[0-9a-zA-Z]{22})$', search_input)
    album_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/album/(?P<AlbumID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    playlist_uri_search = re.search(
        r'^spotify:playlist:(?P<PlaylistID>[0-9a-zA-Z]{22})$', search_input)
    playlist_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/playlist/(?P<PlaylistID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    episode_uri_search = re.search(
        r'^spotify:episode:(?P<EpisodeID>[0-9a-zA-Z]{22})$', search_input)
    episode_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/episode/(?P<EpisodeID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    show_uri_search = re.search(
        r'^spotify:show:(?P<ShowID>[0-9a-zA-Z]{22})$', search_input)
    show_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/show/(?P<ShowID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    artist_uri_search = re.search(
        r'^spotify:artist:(?P<ArtistID>[0-9a-zA-Z]{22})$', search_input)
    artist_url_search = re.search(
        r'^(https?://)?open\.spotify\.com/artist/(?P<ArtistID>[0-9a-zA-Z]{22})(\?si=.+?)?$',
        search_input,
    )

    return (
        extract_info_from_regex_response(TRACK_ID, track_uri_search, track_url_search),

        extract_info_from_regex_response(ALBUM_ID, album_uri_search, album_url_search),

        extract_info_from_regex_response(PLAYLIST_ID, playlist_uri_search, playlist_url_search),

        extract_info_from_regex_response(EPISODE_ID, episode_uri_search, episode_url_search),

        extract_info_from_regex_response(SHOW_ID, show_uri_search, show_url_search),

        extract_info_from_regex_response(ARTIST_ID, artist_uri_search, artist_url_search)
    )


def extract_info_from_regex_response(key, uri_data: Match[str], url_data: Match[str]):
    if uri_data or url_data:
        return (uri_data if uri_data else url_data).group(key)
    else:
        return None
