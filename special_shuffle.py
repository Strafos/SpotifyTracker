import random
import sys
from pprint import pprint
import time

import spotipy
import spotipy.util as util

from entities import Track

scope = 'user-modify-playback-state user-read-currently-playing'

# My Spotify playlist and user ID
AT_PLAYLIST = 'spotify:user:1253958435:playlist:6xaWDZ7I9k7rloD8Ptekbf'
username = '1253958435'

def grab_playlist(client, playlists):
    """Grab all songs form a playlist"""
    tracks = []
    offset = 100
    response = client.user_playlist_tracks(user=username, playlist_id=AT_PLAYLIST, limit=100, offset=offset)
    items = response.get('items', None)
    while items:
        offset += 100
        for item in items:
            tracks.append(Track(item))
        response = client.user_playlist_tracks(user=username, playlist_id=AT_PLAYLIST, offset=offset)
        items = response.get('items', None)
    return tracks

def bucket_by_artists(tracks):
    """Dictionary mapping artist to songs by artist"""
    artist_map = {}
    for track in tracks:
        for artist in track.artists:
            if artist.name in artist_map:
                artist_map[artist.name].add(track)
            else:
                artist_map[artist.name] = set([track])
    return artist_map

def get_connection(username, scope):
    """Connect to spotify API. Key/Secrets are passed as environmental variables"""
    token = util.prompt_for_user_token(username, scope)
    client = spotipy.Spotify(auth=token)
    return client

def get_random_track(artist_map):
    """Get random track from a random artist"""
    random_artist = random.choice(list(artist_map.keys()))
    while len(artist_map[random_artist]) < 5:
        random_artist = random.choice(list(artist_map.keys()))
    random_track = random.sample(artist_map[random_artist], 1)
    return random_track

def get_top_tracks(client):
    tracks = client.current_user_top_tracks(limit=100, time_range="short_term")["items"]
    for track in tracks:
        if str(track['artists'][0]['name'].encode('utf-8')).startswith("b'B"):
            print("%s by %s" % ((track['name'].encode('utf-8')), track['artists'][0]['name'].encode('utf-8')))
        # print(track['artists'][0]['name'].encode('utf'))

def main():
    client = get_connection(username, scope)
    # pprint(client.me())
    get_top_tracks(client)
    return
    tracks = grab_playlist(client, AT_PLAYLIST)
    artist_map = bucket_by_artists(tracks)
    random_tracks = []
    for i in range(100):
        random_tracks += get_random_track(artist_map)

    print([track.name for track in random_tracks])
    track_uris = [track.uri for track in random_tracks if 'local' not in track.uri]
    response = client.start_playback(uris=track_uris)

main()
# res = sp.current_user_playing_track()
# res = sp.next_track()
