gpmdp-cli
===

`gpmdp-cli` is a CLI client for
[Google Play Music Desktop Player](https://www.googleplaymusicdesktopplayer.com/). The client interfaces with the
[Playback Websocket API](https://github.com/MarshallOfSound/Google-Play-Music-Desktop-Player-UNOFFICIAL-/blob/master/docs/PlaybackAPI_WebSocket.md)
 of GPMDP.

# Installation
`gpmdp-cli` requires python 3.5 or greater to run.

dependencies can be found in `requirements.txt` and can be installed with the
following command:
```
pip install -r requirements.txt
```

# Setup
## Enable Playback API
You must enable the Playback API in the `Desktop Settings` of GPMDP. It's a
checkbock in the `General` section.
## Authenticating
When you first use the client a UI will popup in GPMDP containing a 4 digit
code. This code must be entered into `gpmdp-cli` when prompted to authorize the
 client to control GPMDP. A message should pop up in GPMDP when `gpmdp-cli`
has taken control.

# Usage
```
usage: gpmdp-cli [-h] [--token-file TOKEN_FILE]
                 [--socket-server SOCKET_SERVER]
                 commands

Google Play Desktop Music Player CLI client

positional arguments:
  commands              API commands that will be sent to the socket server

optional arguments:
  -h, --help            show this help message and exit
  --token-file TOKEN_FILE
                        Path to token file
  --socket-server SOCKET_SERVER
                        URL to socket server

```

## Examples
Here are some examples of commands
### Toggle Play/Pause
```
python3 gpmdp-cli.py "playback playPause"
```

### Play Next Song
```
python3 gpmdp-cli.py "playback forward"
```

### Play Previous Song
```
python3 gpmdp-cli.py "playback rewind"
```

### Play Song From Start
```
python3 gpmdp-cli.py "playback setCurrentTime [0]"
```

### Toggle Thumps Up Rating On Current Song
```
python3 gpmdp-cli.py "rating toggleThumbsUp"
```

### Increase The Volume By 5
```
python3 gpmdp-cli.py "volume increaseVolume [5]"
```

Further documentation of the API can be found [Here](https://github.com/gmusic-utils/gmusic.js#documentation)

# Author
* Glitch <Glitch@Glitch.is>
