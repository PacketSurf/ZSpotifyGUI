# Introduction

Below will contain sets of errors that you might get running zspotify. Below will also contain possible fixes to these errors. It is advisable that you read this before posting your error in any support channel.

## AttributeError: module 'google.protobuf.descriptor' has no attribute '\_internal_create_key

_Answer(s):_

`pip install --upgrade protobuf`

## FileNotFoundError: Could not find module C:\\path\\to\\libvlc.dll

_Answer(s):_

After installing VLC from [videolan.org](https://www.videolan.org/) it may be necessary to reboot your computer.
It's been reported by Windows users that installing VLC from the Microsoft store helped solved their issues.

## OSError: [WinError 193] %1 is not a valid Win32 application

_Answer(s):_
It's possible you installed the 32bit version of VLC instead of 64bit. Please make ensure you download the correct version from [videolan.org](https://www.videolan.org/)