import random
import sys
from pprint import pprint
import time
from collections import defaultdict

import spotipy
import spotipy.util as util

from entities import Track

scope = 'user-modify-playback-state user-read-currently-playing'

# My Spotify playlist and user ID
# AT_PLAYLIST = 'spotify:user:1253958435:playlist:6xaWDZ7I9k7rloD8Ptekbf'
TEST_PLAYLIST = 'spotify:user:1253958435:playlist:2u470j1YXuPkTOAJfJYytB'
username = '1253958435'


def get_connection(username, scope):
    """Connect to spotify API. Key/Secrets are passed as environmental variables"""
    token = util.prompt_for_user_token(username, scope)
    client = spotipy.Spotify(auth=token)
    return client


def grab_playlist(client, playlists):
    """Grab all songs form a playlist
    return a list of Track objects"""
    tracks = []
    offset = 100
    response = client.user_playlist_tracks(
        user=username, playlist_id=TEST_PLAYLIST, limit=100, offset=offset)
    items = response.get('items', None)
    while items:
        offset += 100
        for item in items:
            tracks.append(Track(item))
        response = client.user_playlist_tracks(
            user=username, playlist_id=TEST_PLAYLIST, offset=offset)
        items = response.get('items', None)
    return tracks


def get_data():
    client = get_connection(username, scope)
    tracks = grab_playlist(client, TEST_PLAYLIST)

    data = {track.uri: track.name for track in tracks}

    freq = defaultdict(int)
    with open("uris.log", "r") as f:
        bad = 0
        good = 0
        for line in f.readlines():
            uri = line.strip()
            if uri in data:
                good += 1
            else:
                if "local" in uri:
                    continue
                # res = client.track(uri)
                # print(res["name"])
                bad += 1
        print(good)
        print(bad)

    # return freq, len(tracks)


get_data()


def test():
    client = get_connection(username, scope)
    tracks = grab_playlist(client, TEST_PLAYLIST)
    print(len(tracks))

    foo = defaultdict(int)
    count = 0
    for track in tracks:
        if not track.id:
            count += 1
            print(track.name)
    print(count)
    # data = [track.id for track in tracks]
    # for i in data:
    #     print(i)
    #     if i in foo:
    #         res = client.track(i)
    #         pprint(res)
    #     else:
    #         foo[i] = 1
    # print("foo")
    # print(len(data))


# test()
