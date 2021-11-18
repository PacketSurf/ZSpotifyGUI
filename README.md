
# ZSpotifyGUI

### A user-friendly desktop app for ZSpotify music downloader for Windows, MacOs, and Linux

<p align="center">
  <img src="https://user-images.githubusercontent.com/12180913/138040605-c9d46e45-3830-4a4b-a7ac-c56bb0d76335.png">
</p>

[Discord Server](https://discord.gg/skVNQKtyFq) - [Matrix Server](https://matrix.to/#/#zspotify:matrix.org) - [Gitea Mirror](https://git.robinsmediateam.dev/Footsiefat/zspotify) - [Main Site](https://footsiefat.github.io/)



Take full advantage of the power of ZSpotify with this graphical interface.
- Find the music you want faster and easier.
- Listen to your music directly in ZSpotify with it's fully featured music player.
- Continue to search for music while downloading.
- Queue up downloads so you can maximise your potential.
- Your spotify likes and playlists sync into the client, allowing you to easily download them
- Easily change settings such as real-time-download, download format, download directory, and search results

<br/>
<br/>
<h3>EASY INSTALLATION</h3>


WINDOWS:
  - Download the latest windows installer from [Releases](https://github.com/PacketSurf/releases).
  - Run the installer and follow the installation instructions.
  - You will find ZSpotify in your start menu, and Desktop (if chosen).


MAC:
  - Download the latest mac zip file from [Releases](https://github.com/PacketSurf/releases).
  - If you don't have VLC installed already, be sure to get the version packaged with VLC included.
  - Make sure the zip file you downloaded is inside your Downloads folder.
  - Open the Terminal application and paste the following exactly:
  ```
  cd Downloads/;unzip ZSpotifyMacOs.zip; cd ZSpotify/;sudo chmod u+x install.sh;./install.sh
  ```
  - You will be asked to enter a password to complete the installation. Please note that when typing your password, nothing     will appear on screen. Just type the password and press enter, and if it is valid the installation will continue.
  - You will find the ZSpotify launcher in your Applications folder, or alternatively in the ZSpotify folder located in your Home folder

<br/>
<br/>

<h4>Command Line Usage</h4>
Alternatively, you may also launch the program directly. Within the zspotify directory run:
```
python3 zspotify/appGui.py
```
or from within the internal zspotify directory:
```
python3 appGui.py
```
<br/>
<br/>
```

### Docker Usage

```
Pull the official docker image (automatically updates):
  docker pull cooper7692/zspotify-docker
Or build the docker image yourself from the Dockerfile:
  docker build -t zspotify .
Create and run a container from the image:
  docker run --rm -v "$PWD/ZSpotify Music:/ZSpotify Music" -v "$PWD/ZSpotify Podcasts:/ZSpotify Podcasts" -it zspotify
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

### Why is my program freezing/why are search results not showing up"?

There are currently some issues with losing connection to the Spotify API. Unfortunately until we can find a fix, your best option is to restart the program, and it will work correctly again. If problems persist, please contact us at the Discord server.

### Contributing

Please refer to [CONTRIBUTING](CONTRIBUTING.md)

### Changelog

Please refer to [CHANGELOG](CHANGELOG.md)

### Common Errors

Please refer to [COMMON_ERRORS](COMMON_ERRORS.md)
