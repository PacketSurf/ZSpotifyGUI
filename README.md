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

Extra command line options:
  -p, --playlist       Downloads a saved playlist from your account
  -ls, --liked-songs   Downloads all the liked songs from your account
  -s, --search         Loads search prompt to find then download a specific track, album or playlist
  -ns, --no-splash     Suppress the splash screen when loading.

Options that can be configured in zs_config.json:
  ROOT_PATH           Change this path if you don't like the default directory where ZSpotify saves the music
  ROOT_PODCAST_PATH   Change this path if you don't like the default directory where ZSpotify saves the podcasts

  SKIP_EXISTING_FILES Set this to false if you want ZSpotify to overwrite files with the same name rather than skipping the song

  MUSIC_FORMAT        Can be "mp3" or "ogg", mp3 is required for track metadata however ogg is slightly higher quality as it is not transcoded.

  FORCE_PREMIUM       Set this to true if ZSpotify isn't automatically detecting that you are using a premium account

  ANTI_BAN_WAIT_TIME  Change this setting if the time waited between bulk downloads is too high or low
  OVERRIDE_AUTO_WAIT  Change this to true if you want to completely disable the wait between songs for faster downloads with the risk of instability
```

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
