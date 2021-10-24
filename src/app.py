import sys

from librespot.audio.decoders import AudioQuality
from tabulate import tabulate

from album import download_album, download_artist_albums
from const import TRACK, NAME, ID, ARTISTS, ITEMS, TRACKS, EXPLICIT, ALBUMS, OWNER, \
    PLAYLISTS, DISPLAY_NAME
from playlist import download_from_user_playlist, download_playlist, \
    download_playlist_with_id
from podcast import download_episode, get_show_episodes
from track import download_track, get_saved_tracks
from utils import splash, split_input, regex_input_for_urls
from zspotify import ZSpotify

SEARCH_URL = 'https://api.spotify.com/v1/search'


def client() -> None:
    """ Connects to spotify to perform query's and get songs to download """
    ZSpotify()
    splash()

    if ZSpotify.check_premium():
        print('[ DETECTED PREMIUM ACCOUNT - USING VERY_HIGH QUALITY ]\n\n')
        ZSpotify.DOWNLOAD_QUALITY = AudioQuality.VERY_HIGH
    else:
        print('[ DETECTED FREE ACCOUNT - USING HIGH QUALITY ]\n\n')
        ZSpotify.DOWNLOAD_QUALITY = AudioQuality.HIGH

    while True:
        if len(sys.argv) > 1:
            process_args_input()
        else:
            search_text = ''
            while len(search_text) == 0:
                search_text = input('Enter search or URL: ')
            process_url_input(search_text, call_search=True)
    # wait()


def process_args_input():
    if sys.argv[1] == '-p' or sys.argv[1] == '--playlist':
        download_from_user_playlist()
    elif sys.argv[1] == '-ls' or sys.argv[1] == '--liked-songs':
        for song in get_saved_tracks():
            if not song[TRACK][NAME]:
                print('###   SKIPPING:  SONG DOES NOT EXISTS ON SPOTIFY ANYMORE   ###')
            else:
                download_track(song[TRACK][ID], 'Liked Songs/')
            print('\n')
    else:
        process_url_input(sys.argv[1])


def process_url_input(url, call_search=False):
    track_id, album_id, playlist_id, episode_id, show_id, artist_id = regex_input_for_urls(url)

    if track_id:
        download_track(track_id)
    elif artist_id:
        download_artist_albums(artist_id)
    elif album_id:
        download_album(album_id)
    elif playlist_id:
        download_playlist_with_id(playlist_id)
    elif episode_id:
        download_episode(episode_id)
    elif show_id:
        for episode in get_show_episodes(show_id):
            download_episode(episode)
    elif call_search:
        search(url)


def search(search_term):
    """ Searches Spotify's API for relevant data """
    params = {'limit': '10', 'offset': '0', 'q': search_term, 'type': 'track,album,artist,playlist'}
    resp = ZSpotify.invoke_url_with_params(SEARCH_URL, **params)

    total_tracks = total_albums = total_artists = 0
    counter = 1
    tracks = resp[TRACKS][ITEMS]
    if len(tracks) > 0:
        print('###  TRACKS  ###')
        track_data = []
        for track in tracks:
            explicit = '[E]' if track[EXPLICIT] else ''
            track_data.append([counter, f'{track[NAME]} {explicit}',
                               ','.join([artist[NAME] for artist in track[ARTISTS]])])
            counter += 1
        total_tracks = counter - 1
        print(tabulate(track_data, headers=['S.NO', 'Name', 'Artists'], tablefmt='pretty'))
        print('\n')

    albums = resp[ALBUMS][ITEMS]
    if len(albums) > 0:
        print('###  ALBUMS  ###')
        album_data = []
        for album in albums:
            album_data.append([counter, album[NAME], ','.join([artist[NAME] for artist in album[ARTISTS]])])
            counter += 1
        total_albums = counter - total_tracks - 1
        print(tabulate(album_data, headers=['S.NO', 'Album', 'Artists'], tablefmt='pretty'))
        print('\n')

    artists = resp[ARTISTS][ITEMS]
    if len(artists) > 0:
        print('###  ARTISTS  ###')
        artist_data = []
        for artist in artists:
            artist_data.append([counter, artist[NAME]])
            counter += 1
        total_artists = counter - total_tracks - total_albums - 1
        print(tabulate(artist_data, headers=['S.NO', 'Name'], tablefmt='pretty'))
        print('\n')

    playlists = resp[PLAYLISTS][ITEMS]
    print('###  PLAYLISTS  ###')
    playlist_data = []
    for playlist in playlists:
        playlist_data.append([counter, playlist[NAME], playlist[OWNER][DISPLAY_NAME]])
        counter += 1
    print(tabulate(playlist_data, headers=['S.NO', 'Name', 'Owner'], tablefmt='pretty'))
    print('\n')
    perform_action(tracks, albums, playlists, artists, total_tracks, total_albums, total_artists)


def perform_action(tracks: list, albums: list, playlists: list, artists: list, total_tracks: int, total_albums: int,
                   total_artists: int):
    if len(tracks) + len(albums) + len(playlists) == 0:
        print('NO RESULTS FOUND - EXITING...')
    else:
        selection = ''
        while len(selection) == 0:
            selection = str(input('SELECT ITEM(S) BY S.NO: '))
        inputs = split_input(selection)
        for pos in inputs:
            position = int(pos)
            if position <= total_tracks:
                track_id = tracks[position - 1][ID]
                download_track(track_id)
            elif position <= total_albums + total_tracks:
                download_album(albums[position - total_tracks - 1][ID])
            elif position <= total_artists + total_tracks + total_albums:
                download_artist_albums(artists[position - total_tracks - total_albums - 1][ID])
            else:
                download_playlist(playlists, position - total_tracks - total_albums - total_artists)


if __name__ == '__main__':
    client()
