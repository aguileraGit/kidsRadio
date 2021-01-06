import tekore as tk
import signal
import phatbeat

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

        #Init volume variables
        self.volumeUpperLimit = 90
        self.volume = None
        self.getVolume()

    #Print playlist
    def printPlaylist(self):
        for items in playList.items:
            print(items.track.name, items.track.id)


    #Check for active device. Returns False if no device is active
    def areDevicesActive(self):
        #Get all possible devices that could be using Spotify
        devices = self.spotify.playback_devices()

        for device in devices:
            print(device)
            #Ignore if the kids radio is playing
            if device.is_active and device.id != self.rPiSpotifyDevice:
                return True

        return False


    #Check to see if track is playing on radio. Returns True if active
    def isActive(self):
        devices = self.spotify.playback_devices()

        for device in devices:
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


### App Functions - Required to easily use the button decorators ###

def printMenu():
    print('h: Help\np: Pause/Play\nn: Next')

@phatbeat.on(phatbeat.BTN_PLAYPAUSE)
def playPause(pin):
    global status
    #Before taking any action, check to see if somebody else is using Spotify
    if radio.areDevicesActive() == False:

        #Get volume
        radio.getVolume()

        #Radio is free
        if status == 'pause':
            status = 'play'
            #Check to see if kids previously paused the radio
            if radio.isActive():
                radio.spotify.playback_resume()
            else:
                radio.loadShuffleAndPlay()
        else:
            status = 'pause'
            #Need to get position
            currentPostion = radio.spotify.playback_currently_playing().timestamp
            radio.spotify.playback_pause(radio.rPiSpotifyDevice)

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

@phatbeat.on(phatbeat.BTN_VOLUP)
def volumeUp(pin):
    radio.increaseVolume(10)

@phatbeat.on(phatbeat.BTN_VOLDN)
def volumeDown(pin):
    radio.decreaseVolume(10)

#### App Start ####
radio = kidsRadioApp()

#Set volume
radio.setVolume(50)

#global status
status = 'pause'

#Pause and wait for buttons
signal.pause()


'''
#Test app by using the keyboard
inputChar = 'p'
status = 'pause'

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
