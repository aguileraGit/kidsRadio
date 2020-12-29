import tekore as tk

file = 'tekore.cfg'
conf = tk.config_from_file(file, return_refresh=True)
token = tk.refresh_user_token(*conf[:2], conf[3])

spotify = tk.Spotify(token)

#print(spotify.current_user())

devices = spotify.playback_devices()

for device in devices:
    print(device)


#https://open.spotify.com/user/thenanny88/playlist/3VPvARnKfvvXJ9egnKcnVG?si=Ov0kyqggSVuSma2GEVz2LQ
kidsPlayList = '3VPvARnKfvvXJ9egnKcnVG'

playList =  spotify.playlist_items(kidsPlayList)

print(playList)

for items in playList.items:
    print(items.track.name, items.track.id)


#Play
spotify.playback_start_tracks(['6xxCQxdGDb6tnoQeHQ1RRD'],0 ,0, '98bb0735e28656bac098d927d410c3138a4b5bca')

spotify.playback_volume(10, '98bb0735e28656bac098d927d410c3138a4b5bca')
