from tqdm import tqdm

from const import ITEMS, ID, TRACK, NAME
from track import download_track
from utils import sanitize_data
from zspotify import ZSpotify

MY_PLAYLISTS_URL = 'https://api.spotify.com/v1/me/playlists'
PLAYLISTS_URL = 'https://api.spotify.com/v1/playlists'


def get_all_playlists():
    """ Returns list of users playlists """
    playlists = []
    limit = 50
    offset = 0

    while True:
        resp = ZSpotify.invoke_url_with_params(MY_PLAYLISTS_URL, limit=limit, offset=offset)
        offset += limit
        playlists.extend(resp[ITEMS])
        if len(resp[ITEMS]) < limit:
            break

    return playlists


def get_playlist_songs(playlist_id):
    """ returns list of songs in a playlist """
    songs = []
    offset = 0
    limit = 100

    while True:
        resp = ZSpotify.invoke_url_with_params(f'{PLAYLISTS_URL}/{playlist_id}/tracks', limit=limit, offset=offset)
        offset += limit
        songs.extend(resp[ITEMS])
        if len(resp[ITEMS]) < limit:
            break

    return songs


def get_playlist_info(playlist_id):
    """ Returns information scraped from playlist """
    resp = ZSpotify.invoke_url(f'{PLAYLISTS_URL}/{playlist_id}?fields=name,owner(display_name)&market=from_token')
    return resp['name'].strip(), resp['owner']['display_name'].strip()


def download_playlist(playlist):
    """Downloads all the songs from a playlist"""

    playlist_songs = [song for song in get_playlist_songs(playlist[ID]) if song[TRACK][ID]]
    p_bar = tqdm(playlist_songs, unit='song', total=len(playlist_songs), unit_scale=True)
    for song in p_bar:
        download_track(song[TRACK][ID], sanitize_data(playlist[NAME].strip()) + '/',
                       disable_progressbar=True)
        p_bar.set_description(song[TRACK][NAME])


def download_from_user_playlist():
    """ Select which playlist(s) to download """
    playlists = get_all_playlists()

    count = 1
    for playlist in playlists:
        print(str(count) + ': ' + playlist[NAME].strip())
        count += 1

    print('\n> SELECT A PLAYLIST BY ID')
    print('> SELECT A RANGE BY ADDING A DASH BETWEEN BOTH ID\'s')
    print('> For example, typing 10 to get one playlist or 10-20 to get\nevery playlist from 10-20 (inclusive)\n')

    playlist_choices = input('ID(s): ').split('-')

    if len(playlist_choices) == 1:
        download_playlist(playlists, playlist_choices[0])
    else:
        start = int(playlist_choices[0])
        end = int(playlist_choices[1]) + 1

        print(f'Downloading from {start} to {end}...')

        for playlist_number in range(start, end):
            download_playlist(playlists, playlist_number)

        print('\n**All playlists have been downloaded**\n')
