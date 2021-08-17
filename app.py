import tekore as tk
import signal
import threading
import phatbeat
import time as timeOG #Need to clean this up. Using import below.
from datetime import datetime, time

print('Starting....')

class kidsRadioApp:

    def __init__(self):
        file = 'tekore.cfg'
        conf = tk.config_from_file(file, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])

        self.spotify = tk.Spotify(token)

        #ID for the kids Radio
        self.rPiSpotifyDevice = '98bb0735e28656bac098d927d410c3138a4b5bca'

        #Name of playlist to choose songs from
        #Named KidsRadioPlaylist on the Spotify App
        self.kidsPlayList = '4CmKflD5wTahQ3iNJCMu2j'

        #Init volume variables and set volume
        self.volumeUpperLimit = 80
        self.volume = 0
        #self.setVolume() #Crashes if RPI isn't found

        #Paused information
        self.pausedTrackID = None
        self.pausedPosition = None

    #Print playlist
    def printPlaylist(self):
        for items in playList.items:
            print(items.track.name, items.track.id)


    #Check for active device. Returns False if no device is active
    def areOtherDevicesActive(self):
        #Get all possible devices that could be using Spotify
        devices = self.spotify.playback_devices()

        for device in devices:
            #print(device)
            #Ignore if the kids radio is playing
            #if device.is_active and device.id != self.rPiSpotifyDevice:
            #    return True

            #Check to see if the device is actually playing something
            if (device.Spotify.playback_currently_playing.is_playing) and\
               (device.id != self.rPiSpotifyDevice):
                return True

        return False


    #Check to see if RPi is available. Returns True if present
    def isKidsRadioPresent(self):
        devices = self.spotify.playback_devices()

        for device in devices:
            #Ignore if the kids radio is playing
            if device.id != self.rPiSpotifyDevice:
                return True

        return False



    #Check to see if track is playing on kids' radio. Returns True if active
    def isTrackActive(self):
        devices = self.spotify.playback_devices()

        for device in devices:
            #print(device)
            if device.id == self.rPiSpotifyDevice:
                if device.is_active == True:
                    return True
        return False


    #Shuffle playlist and start a song
    def loadShuffleAndPlay(self):
        self.setToShuffle()
        playlistURI = tk.to_uri('playlist', self.kidsPlayList)
        self.spotify.playback_start_context(playlistURI, 0, 0, self.rPiSpotifyDevice)


    def setToShuffle(self):
        self.spotify.playback_shuffle(True, self.rPiSpotifyDevice)

    #Get volume for device
    def getVolume(self):
        devices = self.spotify.playback_devices()

        for device in devices:
            if device.id == self.rPiSpotifyDevice:
                self.volume = int(device.volume_percent)
                print('Volume: ', self.volume)


    def increaseVolume(self, amount):
        #See if limit is reached
        if self.volume + amount > self.volumeUpperLimit:
            self.volume = self.volumeUpperLimit
        else:
            self.volume = self.volume + amount

        self.setVolume()


    def decreaseVolume(self, amount):
        #See if limit is reached
        if self.volume - amount <= 0:
            self.volume = 0
        else:
            self.volume = self.volume - amount

        self.setVolume()


    def setVolume(self):
        self.spotify.playback_volume(self.volume, self.rPiSpotifyDevice)


    def saveData(self):
        current = radio.spotify.playback_currently_playing()
        self.pausedPosition = current.progress_ms
        self.pausedTrackID = current.item.id

        print('Saving: ', self.pausedTrackID, self.pausedPosition)


#Create a timer. Used to constantly know the current song and position when
# playing. If Mom or Dad take over, the rPi will no longer be active. Without
# this timer, the app isn't aware it's been disconnected.
class RepeatingTimer(threading.Thread):
    def __init__(self, interval_seconds, callback):
        super().__init__()
        self.stop_event = threading.Event()
        self.interval_seconds = interval_seconds
        self.callback = callback
        self.daemon = False

    def run(self):
        while not self.stop_event.wait(self.interval_seconds):
            self.callback()

    def stop(self):
        self.stop_event.set()


### App Functions - Required to easily use the button decorators ###

def printMenu():
    print('h: Help\np: Pause/Play\nn: Next')


@phatbeat.on(phatbeat.BTN_PLAYPAUSE)
def playPause(pin):
    global status, checkStatusBackground, radio

    #Before taking any action, check to see if somebody else is using Spotify
    # Also check time
    if (radio.areOtherDevicesActive() == False) and
       (is_time_between(allowedTimeOn, allowedTimeOff) == True):

        #Get volume
        radio.getVolume()

        #Radio is free
        if status == 'pause':
            status = 'play'
            #Check to see if kids previously paused the radio and resume
            if radio.isTrackActive():
                print('Resuming from paused state...')
                radio.spotify.playback_seek(radio.pausedPosition, radio.rPiSpotifyDevice)
                radio.spotify.playback_resume()

            else:
                radio.loadShuffleAndPlay()

        elif status == 'play':
            status = 'pause'
            #Get current song and position
            radio.saveData()
            radio.spotify.playback_pause(radio.rPiSpotifyDevice)

        elif status == 'init':
            status = 'play'
            radio.loadShuffleAndPlay()

        print(status)

    #Sombody is using Spotify.
    else:
        print('Spotify is being used by Mom or Dad')


@phatbeat.on(phatbeat.BTN_FASTFWD)
def nextTrack(pin):
    print('Next')
    radio.spotify.playback_next(radio.rPiSpotifyDevice)

@phatbeat.on(phatbeat.BTN_REWIND)
def previousTrack(pin):
    print('Previous')
    radio.spotify.playback_previous(radio.rPiSpotifyDevice)

def exitApp():
    print('Exit')
    checkStatusBackground.stop()

@phatbeat.on(phatbeat.BTN_VOLUP)
def volumeUp(pin):
    radio.increaseVolume(10)

@phatbeat.on(phatbeat.BTN_VOLDN)
def volumeDown(pin):
    radio.decreaseVolume(10)

def updateStatus():
    global status, radio
    print('Background Check')

    #Per note below. If parents have taken over Spotify, save and pause
    if radio.areOtherDevicesActive() == True:
        print('Parents took over')
        status = 'pause'

    #If the current device is active
    if radio.isTrackActive():
        #Save the current song ID and postion
        radio.saveData()
    else:
        #If not active, set the app status to pause
        print('Device not active. Pausing...')
        status = 'pause'

#Helper function to make sure the radio isn't on too early or late
# https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


#### App Start ####
radio = kidsRadioApp()

#Check to make sure device is present. Failure crashes app.
while( radio.isKidsRadioPresent() == False ):
    timeOG.sleep(15)

#Set volume
radio.volume = 0
radio.setVolume()


#Ensure Shuffle is on
radio.setToShuffle()

#global status
status = 'init'

#Put time limits
allowedTimeOn = time(8,0)
allowedTimeOff = time(19,15)

#Background Thread - Runs every few seconds and gets the last song and position
# of the song being played. If the device is no longer active (aka been taken
# over by a parent), it sets the status pause. When the Play/Pause button is
# pressed, it will (1) check to see if it's free and (2) resume song from the
# queue.

checkStatusBackground = RepeatingTimer(3, updateStatus)
checkStatusBackground.start()

#Pause and wait for buttons
signal.pause() #Uncomment when using buttons

#Comment block below when using buttons
'''
inputChar = 'p'

while inputChar != 'x':

    inputChar = input("Press letter: ")

    #Help Menu
    if inputChar == 'h':
        printMenu()

    #Play/Pause
    elif inputChar == 'p':
        playPause()

    #Next track
    elif inputChar == 'n':
        nextTrack()

    #Previous track
    elif inputChar == 'v':
        previousTrack()

    #Exit
    elif inputChar == 'x':
        exitApp()

    #Volume Up
    elif inputChar == 'u':
        volumeUp()

    #Volume Down
    elif inputChar == 'd':
        volumeDown()

    else:
        print('Unknown')
'''
