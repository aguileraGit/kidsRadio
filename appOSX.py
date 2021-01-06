import tekore as tk
import signal
import threading

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
        self.setVolume()

        #Paused information
        self.pausedTrackID = None
        self.pausedPosition = None

    #Print playlist
    def printPlaylist(self):
        for items in playList.items:
            print(items.track.name, items.track.id)


    #Check for active device. Returns False if no device is active
    def areDevicesActive(self):
        #Get all possible devices that could be using Spotify
        devices = self.spotify.playback_devices()

        for device in devices:
            #print(device)
            #Ignore if the kids radio is playing
            if device.is_active and device.id != self.rPiSpotifyDevice:
                return True

        return False


    #Check to see if track is playing on radio. Returns True if active
    def isActive(self):
        devices = self.spotify.playback_devices()

        for device in devices:
            #print(device)
            if device.id == self.rPiSpotifyDevice:
                if device.is_active == True:
                    return True
            return False


    #Shuffle playlist and start a song
    def loadShuffleAndPlay(self):
        self.spotify.playback_shuffle(True, self.rPiSpotifyDevice)
        playlistURI = tk.to_uri('playlist', self.kidsPlayList)
        self.spotify.playback_start_context(playlistURI, 0, 0, self.rPiSpotifyDevice)


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

#@phatbeat.on(phatbeat.BTN_PLAYPAUSE)
def playPause():
    global status, checkStatusBackground, radio

    #Stop the background task
    #checkStatusBackground.stop()

    #Before taking any action, check to see if somebody else is using Spotify
    if radio.areDevicesActive() == False:

        #Get volume
        radio.getVolume()

        #Radio is free
        if status == 'pause':
            status = 'play'
            #Check to see if kids previously paused the radio and resume
            if radio.isActive():
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

    #checkStatusBackground.start()

#@phatbeat.on(phatbeat.BTN_FASTFWD)
def nextTrack():
    print('Next')
    radio.spotify.playback_next(radio.rPiSpotifyDevice)

#@phatbeat.on(phatbeat.BTN_REWIND)
def previousTrack():
    print('Previous')
    radio.spotify.playback_previous(radio.rPiSpotifyDevice)

def exitApp():
    print('Exit')
    checkStatusBackground.stop()

#@phatbeat.on(phatbeat.BTN_VOLUP)
def volumeUp():
    radio.increaseVolume(10)

#@phatbeat.on(phatbeat.BTN_VOLDN)
def volumeDown():
    radio.decreaseVolume(10)

def updateStatus():
    global status, radio
    print('Background Check')
    #If the current device is active
    if radio.isActive():
        #Save the current song ID and postion
        radio.saveData()
    else:
        #If not active, set the app status to pause
        print('Device not active. Pausing...')
        status = 'pause'


#### App Start ####
radio = kidsRadioApp()

#global status
status = 'init'

#Probably need a background function to catch when Spotify is taken over
# by the parents. Runs every few seconds and gets the last song and position
# of the song being played. If the device is no longer active, it sets the
# status to taken over. When the Play/Pause button is pressed, it will add
# the last song to the queue (and time) and resume.
checkStatusBackground = RepeatingTimer(8, updateStatus)
checkStatusBackground.start()

#Pause and wait for buttons
#signal.pause() #Uncomment when using buttons

#Comment block below when using buttons
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
