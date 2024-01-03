import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
import sys
from tqdm import tqdm

scope = "user-library-read,user-library-modify,playlist-modify-public,playlist-modify-private,playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     trackName, trackId = item['track']['name'], item['track']['id']
#     print(trackName, trackId)
    # print(idx, track['artists'][0]['name'], " – ", track['name'])
# print(json.dumps(results["items"], indent=4))

# print(type(playlists))

# for idx, playlist in enumerate(playlists['items']):
#     # print(playlist['name'] + " " + playlist['owner']["display_name"])
#     print(playlist['name']) if playlist['owner']['display_name'] == "Omer Junedi" else ""


def get_my_playlists(user) -> list:
    playlists = []
    response = sp.current_user_playlists()

    for idx, playlist in enumerate(response['items']):
        playlistName, playlistId = playlist['name'], playlist["id"]
        if playlist['owner']['display_name'] == sp.current_user()["display_name"]:
            playlists.append((playlistName, playlistId))

    return playlists


def get_songs_from_playlist(user, limit_step=100):

    playlists = get_my_playlists(sp)
    allSongs = [] # pair: [name, id]
    
    for playlist in playlists:
        playListName, playListId = playlist
        for offset in range(0, 1100, limit_step):
            response = sp.user_playlist_tracks(
                playlist_id=playListId,
                offset=offset
            )
            if len(response) == 0:
                break

            for idx, item in enumerate(response['items']):
                if item['track'] is not None:
                    trackName, trackId = item['track']['name'], item['track']['uri']
                    allSongs.append([trackName, trackId])
            # print(json.dumps(response['items'], indent=4))
    return allSongs
            

# create hash set of songs "likedSongs" currently in liked songs
def get_all_saved_tracks(user, limit_step=50):
    tracks = [] # pair: [trackName, trackId]
    for offset in range(0, 1000, limit_step):
        response = user.current_user_saved_tracks(
            limit=limit_step,
            offset=offset
        )
        if len(response) == 0:
            break
        for idx, item in enumerate(response['items']):
            trackName, trackId = item['track']['name'], item['track']['uri']
            tracks.append((trackName, trackId)) # tuple because they are hashable
    
    return tracks


def main():
    
    # Do not need to keep track of likedSongs because of current_user_saved_tracks_contains() method
    # however could be useful later for different analyses so I'll keep it around for now
    # likedSongs = get_all_saved_tracks(sp)
    allSongs = get_songs_from_playlist(sp)
    # print(type(allSongs), len(allSongs))
    with open("addedTracks.txt", 'a') as f:
        for trackName, trackId in tqdm(allSongs):
            # print([trackId.removeprefix("spotify:track:")])
            trackId = trackId.removeprefix("spotify:track:")
            # in case of removed tracks, local tracks, or changed IDs
            try:
                # takes in list of ids, and returns list of bools
                if not sp.current_user_saved_tracks_contains([trackId])[0]:
                    print(f"{trackName} was not in liked songs")
                    try: 
                        sp.current_user_saved_tracks_add([trackId])
                    except SpotifyException as e:
                        print("inside exception occured", e, trackName, trackId)
                    f.write(f"Added {trackName}: {trackId} to liked songs!\n")
            except SpotifyException as e:
                print("outside exception occured!", e, trackName, trackId)
    # print(type(sp.current_user_saved_tracks_contains(["2bSk87AVkCIIC3Bcligq1z"])))
    # sp.current_user_saved_tracks_add(["2bSk87AVkCIIC3Bcligq1z"])
    # print(sp.current_user_saved_tracks_contains(["2bSk87AVkCIIC3Bcligq1z"]))



# create one big list of all songs "allSongs" from all my playlists
# iterate through big ass list "allSongs" check against set and add into liked songs (in spotify) accordingly
    # go through each one of my playlists and get the tracks

# making sure to add a song into the set once added to liked songs

main()