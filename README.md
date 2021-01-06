# kidsRadio

## Required Hardware and Software
- HW: Pimoroni Pirate Radio from [Adafruit](https://www.adafruit.com/product/3477)
- SW: [raspotify](https://github.com/dtcooper/raspotify) + this Git Repo + [Tekore](https://tekore.readthedocs.io/en/stable/index.html)
Spotify account

## Setup

### Setup the RPi
Setup the RPi using the [Pimoroni](https://learn.pimoroni.com/tutorial/sandyj/streaming-airplay-to-your-pi) instructions. It will setup the audio, buttons, and leds.

You may need to install the Phat-beat [libraries](https://github.com/pimoroni/phat-beat).

Install Raspotify. This will make the RPi a Spotify Device you can stream to.

### Spotify
Setup Spotify for developers. Get Client ID and Secret.

Create a playlist for the kid's music.

### The fun part
Export your Client ID and Secret as variables to the shell.

Run configTest2.py. This will allow you to login to Spotify and grant the Python app access. This will also create the tekore.cfg file that will allow constant access to the required Tokens.

I ran this on a seperate machine since the RPi is headless. The tekore.cfg file must then be copied over to the RPi via SSH.

**Note you can remove the shell variables at this point**

Edit the self.rPiSpotifyDevice with the ID of the RPi Radio. You can use the configured.py to list all your devices.

Get the playlist name by copying the link (Three dots) from the Spotify App/Web and paste to a text file. Extract the playlist ID (first set of numbers/letters).

## References
- https://github.com/pimoroni/phat-beat/tree/91821cf0ba05465d23c241694ba0b5a66986f711
- https://forums.pimoroni.com/t/phatbeat-library-clash-with-cleanshutdown/6675
- https://stackoverflow.com/questions/47291633/repeating-a-function-in-a-background-thread-every-n-seconds
- 
