
# ZSpotifyGUI

### A user-friendly desktop app built on the ZSpotify music downloader for Windows, MacOs, and Linux

<p align="center">
  <img src="https://user-images.githubusercontent.com/35679186/141209937-049e8a52-95fd-4028-aa6c-d70670cd0171.png">
</p>

[Discord Server](https://discord.gg/skVNQKtyFq) - [Matrix Server](https://matrix.to/#/#zspotify:matrix.org) - [Gitea Mirror](https://git.robinsmediateam.dev/Footsiefat/zspotify) - [Main Site](https://footsiefat.github.io/)



Take full advantage of the power of ZSpotify with this user-friendly graphical interface.
- Find the music you want faster and easier.
- Listen to your music directly in ZSpotify with it's fully featured music player.
- Continue to search for music while downloading.
- Queue up downloads so you can maximise your downloading potential.
- Your spotify likes sync into the client, allowing you to easily download them
- Easily change settings such as real-time-download, download format, download directory, and search results

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
  - (Important) Due to a recent bug fix in one of our dependencies, it is important to update it to the newest version. This will cause major improvements to stability. This can be done by pasting this in CMD: ```pip install --upgrade git+https://github.com/kokarare1212/librespot-python```
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
  - (Important) Due to a recent bug fix in one of our dependencies, it is important to update it to the newest version. This will cause major improvements to stability. This can be done by pasting this in Terminal: ```pip3 install --upgrade git+https://github.com/kokarare1212/librespot-python```

<br/>
<br/>

<h3>MANUAL INSTALLATION</h3>

  - VLC can be installed from [videolan.org](https://www.videolan.org/vlc/) for all operating systems. You will need to restart your pc.
  - ffmpeg can be installed via apt for Debian-based distros or by downloading the binaries from [ffmpeg.org](https://ffmpeg.org) and placing them in your %PATH% in Windows. Mac users can install it with [Homebrew](https://brew.sh) by running `brew install ffmpeg`.
  - Install the python requirements:
  `pip install -r requirements.txt`



<br/>


/*Git can be installed via apt for Debian-based distros or by downloading the binaries from [git-scm.com](https://git-scm.com/download/win) for Windows.


<h2>Usage</h2>

- The primary way to run ZSpotify is by clicking on the launch icon created during the easy installation process. On Windows this is a file called ZSpotify.bat. On Mac this is a file called ZSpotify.command.
- Alternatively you can run the program directly from the terminal by navigating to the folder containing appGui.py and running:
`python appGui.py`
- You may also use the regular ZSpotify CLI as normal.


<h3>Command Line Usage</h3>

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
