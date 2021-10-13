import os
import os.path
import platform

import unicodedata
import re

import subprocess
import time
import sys

import requests

import json

import music_tag

from librespot.audio.decoders import AudioQuality
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.player.codecs import VorbisOnlyAudioQuality

from pydub import AudioSegment

quality: AudioQuality = AudioQuality.HIGH
session: Session = None

import hashlib


rootPath = "ZSpotify Music/"
skipExistingFiles = True


#miscellaneous functions for general use
def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def wait(seconds: int = 3):
    for i in range(seconds)[::-1]:
        print("\rWait for %d second(s)..." % (i + 1), end="")
        time.sleep(1)

def sanitizeData(value):
    return value.replace("\\", "").replace("/", "")

def splash():
    print("=================================\n"
          "| Spotify Downloader            |\n"
          "|                               |\n"
          "| by Footsiefat/Deathmonger     |\n"
          "=================================\n\n\n")



#two mains functions for logging in and doing client stuff
def login():
    global session

    if os.path.isfile("credentials.json"):
        try:
            session = Session.Builder().stored_file().create()
            return
        except RuntimeError:
            pass
    while True:
        user_name = input("UserName: ")
        password = input("Password: ")
        try:
            session = Session.Builder().user_pass(user_name, password).create()
            return
        except RuntimeError:
            pass

def client():
    global quality, session
    splash()
    if len(sys.argv) > 1:
        if sys.argv[1] != "-p" and sys.argv[1] != "--playlist":
            track_uri_search = re.search(
                r"^spotify:track:(?P<TrackID>[0-9a-zA-Z]{22})$", sys.argv[1])
            track_url_search = re.search(
                r"^(https?://)?open\.spotify\.com/track/(?P<TrackID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
                sys.argv[1],
            )
            
            album_uri_search = re.search(
                r"^spotify:album:(?P<AlbumID>[0-9a-zA-Z]{22})$", sys.argv[1])
            album_url_search = re.search(
                r"^(https?://)?open\.spotify\.com/album/(?P<AlbumID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
                sys.argv[1],
            )
            
            playlist_uri_search = re.search(
                r"^spotify:playlist:(?P<PlaylistID>[0-9a-zA-Z]{22})$", sys.argv[1])
            playlist_url_search = re.search(
                r"^(https?://)?open\.spotify\.com/playlist/(?P<PlaylistID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
                sys.argv[1],
            )
            
            if track_uri_search is not None or track_url_search is not None:
                track_id_str = (track_uri_search
                                if track_uri_search is not None else
                                track_url_search).group("TrackID")
                                
                downloadTrack(track_id_str)
            elif album_uri_search is not None or album_url_search is not None:
                album_id_str = (album_uri_search
                                if album_uri_search is not None else
                                album_url_search).group("AlbumID")
                                
                downloadAlbum(album_id_str)
            elif playlist_uri_search is not None or playlist_url_search is not None:
                playlist_id_str = (playlist_uri_search
                                if playlist_uri_search is not None else
                                playlist_url_search).group("PlaylistID")
                                
                token = session.tokens().get("user-read-email")
                playlistSongs = get_playlist_songs(token, playlist_id_str)
                name, creator = get_playlist_info(token, playlist_id_str)
                for song in playlistSongs:
                    downloadTrack(song['track']['id'], name + "/")
                    print("\n")                
        else:
            downloadFromOurPlaylists()
    else:
        searchText = input("Enter search: ")
        search(searchText)
    wait()



#related functions that do stuff with the spotify API
def search(searchTerm):
    token = session.tokens().get("user-read-email")
    
    
    resp = requests.get(
        "https://api.spotify.com/v1/search",
        {
            "limit": "10",
            "offset": "0",
            "q": searchTerm,
            "type": "track,album,playlist"
        },
        headers={"Authorization": "Bearer %s" % token},
    )
    
    i = 1
    tracks = resp.json()["tracks"]["items"]
    if len(tracks) > 0:
        print("###  TRACKS  ###")
        for track in tracks:
            print("%d, %s | %s" % (
                i,
                track["name"],
                ",".join([artist["name"] for artist in track["artists"]]),
            ))
            i += 1
        totalTracks = i - 1
        print("\n")
    else:
        totalTracks = 0
    
    
    albums = resp.json()["albums"]["items"]
    if len(albums) > 0:
        print("###  ALBUMS  ###")
        for album in albums:
            print("%d, %s | %s" % (
                i,
                album["name"],
                ",".join([artist["name"] for artist in album["artists"]]),
            ))
            i += 1
        totalAlbums = i - totalTracks - 1
        print("\n")
    else:
        totalAlbums = 0
    
    
    playlists = resp.json()["playlists"]["items"]
    if len(playlists) > 0:
        print("###  PLAYLISTS  ###")
        for playlist in playlists:
            print("%d, %s | %s" % (
                i,
                playlist["name"],
                playlist['owner']['display_name'],
            ))
            i += 1
        totalPlaylists = i - totalTracks - totalAlbums - 1
        print("\n")
    else:
        totalPlaylists = 0
    
    if len(tracks) + len(albums) + len(playlists) == 0:
        print("NO RESULTS FOUND - EXITING...")
    else:
        position = int(input("SELECT ITEM BY ID: "))
    
        if position <= totalTracks:
            trackId = tracks[position - 1]["id"]
            downloadTrack(trackId)
        elif position <= totalAlbums + totalTracks:
            downloadAlbum(albums[position - totalTracks - 1]["id"])
        else:
            playlistChoice = playlists[position - totalTracks - totalAlbums - 1]
            playlistSongs = get_playlist_songs(token, playlistChoice['id'])
            for song in playlistSongs:
                downloadTrack(song['track']['id'], sanitizeData(playlistChoice['name'].strip()) + "/")
                print("\n")
    
def getSongInfo(songId):
    token = session.tokens().get("user-read-email")
   
    info = json.loads(requests.get("https://api.spotify.com/v1/tracks?ids=" + songId + '&market=from_token', headers={"Authorization": "Bearer %s" % token}).text)
   
    artists = []
    for x in info['tracks'][0]['artists']:
        artists.append(sanitizeData(x['name']))
    albumName = sanitizeData(info['tracks'][0]['album']["name"])
    name = sanitizeData(info['tracks'][0]['name'])
    imageUrl = info['tracks'][0]['album']['images'][0]['url']
    releaseYear = info['tracks'][0]['album']['release_date'].split("-")[0]
    disc_number = info['tracks'][0]['disc_number']
    track_number = info['tracks'][0]['track_number']
    scrapedSongId = info['tracks'][0]['id']

    return artists, albumName, name, imageUrl, releaseYear, disc_number, track_number, scrapedSongId
    
    
    
#Functions directly related to modifying the downloaded audio and its metadata
def convertToMp3(filename):
    print("###   CONVERTING TO MP3   ###")
    raw_audio = AudioSegment.from_file(filename, format="ogg",
                                   frame_rate=44100, channels=2, sample_width=2)
    raw_audio.export(filename, format="mp3")

def setAudioTags(filename, artists, name, albumName, releaseYear, disc_number, track_number):
    print("###   SETTING MUSIC TAGS   ###")
    f = music_tag.load_file(filename)
    f['artist'] = convArtistFormat(artists)
    f['tracktitle'] = name
    f['album'] = albumName
    f['year'] = releaseYear
    f['discnumber'] = disc_number
    f['tracknumber'] = track_number
    f.save()

def setMusicThumbnail(filename, imageUrl):
    print("###   SETTING THUMBNAIL   ###")
    r = requests.get(imageUrl).content
    f = music_tag.load_file(filename)
    f['artwork'] = r
    f.save()
    
def convArtistFormat(artists):
    formatted = ""
    for x in artists:
        formatted += x + ", "
    return formatted[:-2]



#Extra functions directly related to spotify playlists
def get_all_playlists(access_token):
    playlists = []
    limit = 50
    offset = 0
    
    while True:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'limit': limit, 'offset': offset}        
        resp = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers, params=params).json()
        offset += limit
        playlists.extend(resp['items'])

        if len(resp['items']) < limit:
            break

    return playlists

def get_playlist_songs(access_token, playlist_id):
    songs = []
    offset = 0
    limit = 100

    while True:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'limit': limit, 'offset': offset}        
        resp = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, params=params).json()
        offset += limit
        songs.extend(resp['items'])
        
        if len(resp['items']) < limit:
            break

    return songs

def get_playlist_info(access_token, playlist_id):
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}?fields=name,owner(display_name)&market=from_token', headers=headers).json()
        return resp['name'].strip(), resp['owner']['display_name'].strip()


#Extra functions directly related to spotify albums
def get_album_tracks(access_token, album_id):
    songs = []
    offset = 0
    limit = 50

    while True:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'limit': limit, 'offset': offset}        
        resp = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks', headers=headers, params=params).json()
        offset += limit
        songs.extend(resp['items'])
        
        if len(resp['items']) < limit:
            break

    return songs

def get_album_name(access_token, album_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.get(f'https://api.spotify.com/v1/albums/{album_id}', headers=headers).json()
    return resp['artists'][0]['name'], sanitizeData(resp['name'])





#Functions directly related to downloading stuff
def downloadTrack(track_id_str: str, extra_paths = ""):
    global rootPath, skipExistingFiles
    track_id = TrackId.from_base62(track_id_str)
    artists, albumName, name, imageUrl, releaseYear, disc_number, track_number, scrapedSongId = getSongInfo(track_id_str)
    
    songName = artists[0] + " - " + name
    filename = rootPath + extra_paths + songName + '.mp3'
    
    
    skipExistingFiles
    
    if os.path.isfile(filename) and  skipExistingFiles:
        print("###   SKIPPING:", songName, "(SONG ALREADY EXISTS)   ###")
    else:
        if track_id_str != scrapedSongId:
            print("###   APPLYING PATCH TO LET SONG DOWNLOAD   ###")
            track_id_str = scrapedSongId
            track_id = TrackId.from_base62(track_id_str)

        print("###   FOUND SONG:", songName, "   ###")

        stream = session.content_feeder().load(
            track_id, VorbisOnlyAudioQuality(quality), False, None)

   
        print("###   DOWNLOADING RAW AUDIO   ###")

        if not os.path.isdir(rootPath + extra_paths):
            os.makedirs(rootPath + extra_paths)

        with open(filename,'wb') as f:
            chunk_size = 1024 * 16
            buffer = bytearray(chunk_size)
            bpos = 0

            while True:
                byte = stream.input_stream.stream().read()
                
                if byte == -1:
                    # flush buffer before breaking
                    if bpos > 0:
                        f.write(buffer[0:bpos])
                    break

                buffer[bpos] = byte
                bpos += 1

                if bpos == (chunk_size):
                    f.write(buffer)
                    bpos = 0
            
        convertToMp3(filename)
        setAudioTags(filename, artists, name, albumName, releaseYear, disc_number, track_number)
        setMusicThumbnail(filename, imageUrl)

def downloadAlbum(album):
    token = session.tokens().get("user-read-email")
    artist, album_name = get_album_name(token, album)
    tracks = get_album_tracks(token, album)
    for track in tracks:
        downloadTrack(track['id'], artist + " - " + album_name + "/")
        print("\n")

def downloadFromOurPlaylists():
    token = session.tokens().get("user-read-email")
    playlists = get_all_playlists(token)
    
    count = 1
    for playlist in playlists:
        print(str(count) + ": " + playlist['name'].strip())
        count += 1
    
    playlistChoice = input("SELECT A PLAYLIST BY ID: ")
    playlistSongs = get_playlist_songs(token, playlists[int(playlistChoice) - 1]['id'])
    for song in playlistSongs:
    
        downloadTrack(song['track']['id'], sanitizeData(playlists[int(playlistChoice) - 1]['name'].strip()) + "/")
        print("\n")


#Core functions here
def main():
    login()  
    client()

if __name__ == "__main__":
    main()
    
    
#Left over code ill probably want to reference at some point
"""
        if args[0] == "q" or args[0] == "quality":
            if len(args) == 1:
                print("Current Quality: " + quality.name)
                wait()
            elif len(args) == 2:
                if args[1] == "normal" or args[1] == "96":
                    quality = AudioQuality.NORMAL
                elif args[1] == "high" or args[1] == "160":
                    quality = AudioQuality.HIGH
                elif args[1] == "veryhigh" or args[1] == "320":
                    quality = AudioQuality.VERY_HIGH
                print("Set Quality to %s" % quality.name)
                wait()
"""


#TO DO'S:
#MAKE AUDIO SAVING MORE EFFICIENT 