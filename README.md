# kidsRadio

## Required Hardware and Software
HW: Pimoroni Pirate Radio from [Adafruit](https://www.adafruit.com/product/3477)
SW: raspotify + this Git Repo
Spotify account

## Setup

### Setup the RPi
Setup the RPi using the [Pimoroni](https://learn.pimoroni.com/tutorial/sandyj/streaming-airplay-to-your-pi) instructions. It will setup the audio, buttons, and leds.

Install Raspotify. This will make the RPi a Spotify Device you can stream to.

### Spotify
Setup Spotify for developers. Get Client ID and Secret.

Create a playlist for the kid's music.

### The fun part
Export your Client ID and Secret as variables to the shell.

Run configTest2.py. This will allow you to login to Spotify and grant the Python app access. This will also create the tekore.cfg file that will allow constant access to the required Tokens.

**Note you can remove the shell variables at this point**

I ran this on a seperate machine since the RPi is headless. The tekore.cfg file must then be copied over to the RPi via SSH.

Edit the self.rPiSpotifyDevice with the ID of the RPi Radio. You can use the configured.py to list all your devices.

Get the playlist name by copying the link from the Spotify App/Web and paste to a text file. Extract the playlist ID.
