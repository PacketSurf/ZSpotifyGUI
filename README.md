
# ZSpotifyGUI

### A user-friendly desktop app built on the ZSpotify music downloader for Windows, MacOs, and Linux

<p align="center">
  <img src="https://user-images.githubusercontent.com/35679186/141209937-049e8a52-95fd-4028-aa6c-d70670cd0171.png">
</p>

[Discord Server](https://discord.gg/skVNQKtyFq) - [Matrix Server](https://matrix.to/#/#zspotify:matrix.org) - [Gitea Mirror](https://git.robinsmediateam.dev/Footsiefat/zspotify) - [Main Site](https://footsiefat.github.io/)



Take full advantage of the power of ZSpotify with this user-friendly graphical interface.
- Find and download the music you want faster and easier.
- Listen to your music directly in ZSpotify with it's fully featured music player.
- Continue to search for music while downloading.
- Queue up downloads so you can maximise your downloading potential.
- Your spotify likes sync into the client, allowing you to easily download them.
- Easily change settings such as real-time-download, download format, download directory, and search results within the client.

<h3>SCREENSHOTS</h3>
<p align="center">
  <img src="https://user-images.githubusercontent.com/93454665/142783298-9550720a-c5c1-4714-8952-285c852f52d1.png">
</p>

<br/>
<h3>EASY INSTALLATION</h3>


WINDOWS:
  - Download the latest Windows installer from [Releases](https://github.com/PacketSurf/ZSpotifyGUI/releases).
  - Run the installer and follow the installation instructions.
  - You will find ZSpotify in your start menu, and Desktop (if chosen).
  - If you did not have VLC installed already, you will need to restart your PC after installation. If you already had it, then a restart is not necessary.

<br/>

MAC:
  - Download the latest MacOs zip file from [Releases](https://github.com/PacketSurf/ZSpotifyGUI/releases).
  - Make sure the zip file you downloaded is inside your Downloads folder.
  - Open the Terminal application and paste the following command:
  ```
  cd Downloads/;unzip ZSpotifyMacOs.zip; cd ZSpotifyGUI/;sudo chmod u+x install.sh;./install.sh
  ```
  - You will be asked to enter a password to complete the installation. Please note that when typing your password, nothing     will appear on screen. Just type the password and press enter, and if it is valid the installation will continue.
  - You will find the ZSpotify launcher in your Applications folder, or alternatively in the ZSpotify folder located in your Home folder
  - If you did not have VLC installed already, you will need to restart your PC after installation. If you already had it, then a restart is not necessary.


<br/>
<br/>

<h3>MANUAL INSTALLATION</h3>

  - 64bit VLC can be installed from [videolan.org](https://www.videolan.org/vlc/) for all operating systems. You will need to restart your pc. Sometimes the VLC website will automatically download the 32bit version. Please ensure you download the 64bit version
  - ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries from [ffmpeg.org](https://ffmpeg.org) and placing them in your %PATH% in Windows. Mac users can install it with [Homebrew](https://brew.sh) by running `brew install ffmpeg`.
  - Install the python requirements:
  `pip install -r requirements.txt`



<br/>


/*Git can be installed via apt for Debian-based distros or by downloading the binaries from [git-scm.com](https://git-scm.com/download/win) for Windows.


<h2>Usage</h2>

- The primary way to run ZSpotify is by clicking on the launch icon created during the easy installation process. On Windows this is a file called ZSpotify.bat. On Mac this is a file called ZSpotify.command.
- Alternatively you can run the program directly from the terminal by navigating to the source folder containing appGui.py and running:
`python appGui.py`
- You may also use the regular ZSpotify CLI as normal.


<h3>Command Line Usage</h3>

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
<<<<<<< HEAD

Options that can be configured in zs_config.json:
  ROOT_PATH           Change this path if you don't like the default directory where ZSpotify saves the music
  ROOT_PODCAST_PATH   Change this path if you don't like the default directory where ZSpotify saves the podcasts

  SKIP_EXISTING_FILES Set this to false if you want ZSpotify to overwrite files with the same name rather than skipping the song

  MUSIC_FORMAT        Can be "mp3" or "ogg", mp3 is required for track metadata however ogg is slightly higher quality as it is not transcoded.

  FORCE_PREMIUM       Set this to true if ZSpotify isn't automatically detecting that you are using a premium account

  ANTI_BAN_WAIT_TIME  Change this setting if the time waited between bulk downloads is too high or low
  OVERRIDE_AUTO_WAIT  Change this to true if you want to completely disable the wait between songs for faster downloads with the risk of instability

=======
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
>>>>>>> 1585133e70ad6ab21c70e07f5c9d98b1127eca3e

<h4>FAQ<h4/>
```

### Will my account get banned if I use this tool?

~~Currently no user has reported their account getting banned after using ZSpotify.~~

**There have been 2-3 reports from users who received account bans from Spotify for using this tool**.

We recommend using ZSpotify with a burner account.
Alternatively, there is a configuration option labled ```DOWNLOAD_REAL_TIME```, this limits the download speed to the duration of the song being downloaded thus not appearing suspicious to Spotify.
This option is much slower and is only recommended for premium users who wish to download songs in 320kbps without buying premium on a burner account.

**Use ZSpotify at your own risk**, the developers of ZSpotify are not responsible if your account gets banned.

### Why is my program freezing/why are search results not showing up"?

There are currently some issues with losing connection to the Spotify API. Unfortunately until we can find a fix, your best option is to restart the program, and it will work correctly again. If problems persist, please contact us at the Discord server.

### Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)

### Changelog

Please refer to [CHANGELOG](CHANGELOG.md)

### Common Errors

Please refer to [COMMON_ERRORS](COMMON_ERRORS.md)
