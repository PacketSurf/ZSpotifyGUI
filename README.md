![Stars](https://img.shields.io/github/stars/Footsiefat/zspotify.svg)
![Forks](https://img.shields.io/github/forks/Footsiefat/zspotify.svg)
![Size](https://img.shields.io/github/repo-size/Footsiefat/zspotify)

# ZSpotify

### A Spotify downloader needing only a python interpreter and ffmpeg.

<p align="center">
  <img src="https://user-images.githubusercontent.com/35679186/141209937-049e8a52-95fd-4028-aa6c-d70670cd0171.png">
</p>

[Discord Server](https://discord.gg/skVNQKtyFq) - [Matrix Server](https://matrix.to/#/#zspotify:matrix.org) - [Gitea Mirror](https://git.robinsmediateam.dev/Footsiefat/zspotify) - [Main Site](https://footsiefat.github.io/)

```
Requirements:

Binaries

- Python 3.9 or greater
- ffmpeg*
- Git**

Python packages:

- pip install -r requirements.txt

```

\*ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries from [ffmpeg.org](https://ffmpeg.org) and placing them in your %PATH% in Windows. Mac users can install it with [Homebrew](https://brew.sh) by running `brew install ffmpeg`.

\*\*Git can be installed via apt for Debian-based distros or by downloading the binaries from [git-scm.com](https://git-scm.com/download/win) for Windows.

### Command line usage:

```
Basic command line usage:
  python zspotify <track/album/playlist/episode/artist url>   Downloads the track, album, playlist or podcast episode specified as a command line argument. If an artist url is given, all albums by specified artist will be downloaded. Can take multiple urls.

Different usage modes:
  (nothing)            Download the tracks/alumbs/playlists URLs from the parameter
  -d,  --download      Download all tracks/alumbs/playlists URLs from the specified file
  -p,  --playlist      Downloads a saved playlist from your account
  -ls, --liked-songs   Downloads all the liked songs from your account
  -s,  --search        Loads search prompt to find then download a specific track, album or playlist
  
Extra command line options:
  -ns, --no-splash     Suppress the splash screen when loading.
  --config-location    Use a different zs_config.json, defaults to the one in the program directory
```

### Options:

All these options can either be configured in the zs_config or via the commandline, in case of both the commandline-option has higher priority.  
Be aware you have to set boolean values in the commandline like this: `--download-real-time=True`

| Key (zs-config)              | commandline parameter            | Description
|------------------------------|----------------------------------|---------------------------------------------------------------------|
| ROOT_PATH                    | --root-path                      | directory where ZSpotify saves the music
| ROOT_PODCAST_PATH            | --root-podcast-path              | directory where ZSpotify saves the podcasts
| SKIP_EXISTING_FILES          | --skip-existing-files            | Skip songs with the same name
| SKIP_PREVIOUSLY_DOWNLOADED   | --skip-previously-downloaded     | Create a .song_archive file and skip previously downloaded songs
| DOWNLOAD_FORMAT              | --download-format                | The download audio format (aac, fdk_aac, m4a, mp3, ogg, opus, vorbis)
| FORCE_PREMIUM                | --force-premium                  | Force the use of high quality downloads (only with premium accounts)
| ANTI_BAN_WAIT_TIME           | --anti-ban-wait-time             | The wait time between bulk downloads
| OVERRIDE_AUTO_WAIT           | --override-auto-wait             | Totally disable wait time between songs with the risk of instability
| CHUNK_SIZE                   | --chunk-size                     | chunk size for downloading
| SPLIT_ALBUM_DISCS            | --split-album-discs              | split downloaded albums by disc
| DOWNLOAD_REAL_TIME           | --download-real-time             | only downloads songs as fast as they would be played, can prevent account bans
| LANGUAGE                     | --language                       | Language for spotify metadata
| BITRATE                      | --bitrate                        | Overwrite the bitrate for ffmpeg encoding
| SONG_ARCHIVE                 | --song-archive                   | The song_archive file for SKIP_PREVIOUSLY_DOWNLOADED
| CREDENTIALS_LOCATION         | --credentials-location           | The location of the credentials.json
| OUTPUT                       | --output                         | The output location/format (see below)
| PRINT_SPLASH                 | --print-splash                   | Print the splash message
| PRINT_SKIPS                  | --print-skips                    | Print messages if a song is being skipped
| PRINT_DOWNLOAD_PROGRESS      | --print-download-progress        | Print the download/playlist progress bars
| PRINT_ERRORS                 | --print-errors                   | Print errors
| PRINT_DOWNLOADS              | --print-downloads                | Print messages when a song is finished downloading
| TEMP_DOWNLOAD_DIR            | --temp-download-dir              | Download tracks to a temporary directory first

### Output format:

With the option `OUTPUT` (or the commandline parameter `--output`) you can specify the output location and format.  
The value is relative to the `ROOT_PATH`/`ROOT_PODCAST_PATH` directory and can contain the following placeholder:

| Placeholder     | Description
|-----------------|--------------------------------
| {artist}        | The song artist
| {album}         | The song album
| {song_name}     | The song name
| {release_year}  | The song release year
| {disc_number}   | The disc number
| {track_number}  | The track_number
| {id}            | The song id
| {track_id}      | The track id
| {ext}           | The file extension
| {album_id}      | (only when downloading albums) ID of the album
| {album_num}     | (only when downloading albums) Incrementing track number
| {playlist}      | (only when downloading playlists) Name of the playlist 
| {playlist_num}  | (only when downloading playlists) Incrementing track number

Example values could be:
~~~~
{playlist}/{artist} - {song_name}.{ext}
{playlist}/{playlist_num} - {artist} - {song_name}.{ext}
Liked Songs/{artist} - {song_name}.{ext}
{artist} - {song_name}.{ext}
{artist}/{album}/{album_num} - {artist} - {song_name}.{ext}
/home/user/downloads/{artist} - {song_name} [{id}].{ext}
~~~~

### Docker Usage

```
Pull the official docker image (automatically updates):
  docker pull cooper7692/zspotify-docker
Or build the docker image yourself from the Dockerfile:
  docker build -t zspotify .
Create and run a container from the image:
  docker run --rm -u $(id -u):$(id -g) -v "$PWD/zspotify:/app" -v "$PWD/zs_config.json:/zs_config.json" -v "$PWD/ZSpotify Music:/ZSpotify Music" -v "$PWD/ZSpotify Podcasts:/ZSpotify Podcasts" -it zspotify
```

### Google Colab
There is a community maintained repo for Google Colab at [Ori5000/zspotifycolab](https://github.com/Ori5000/zspotifycolab) designed to make it easier to add songs to Google Drive or orther cloud services.

### Will my account get banned if I use this tool?

~~Currently no user has reported their account getting banned after using ZSpotify.~~

**There have been 2-3 reports from users who received account bans from Spotify for using this tool**.

We recommend using ZSpotify with a burner account.
Alternatively, there is a configuration option labled ```DOWNLOAD_REAL_TIME```, this limits the download speed to the duration of the song being downloaded thus not appearing suspicious to Spotify.
This option is much slower and is only recommended for premium users who wish to download songs in 320kbps without buying premium on a burner account.

**Use ZSpotify at your own risk**, the developers of ZSpotify are not responsible if your account gets banned.

### What do I do if I see "Your session has been terminated"?

If you see this, don't worry! Just try logging back in. If you see the incorrect username or password error, reset your password and you should be able to log back in and continue using Spotify.

### Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)

### Changelog

Please refer to [CHANGELOG](CHANGELOG.md)

### Common Errors

Please refer to [COMMON_ERRORS](COMMON_ERRORS.md)
