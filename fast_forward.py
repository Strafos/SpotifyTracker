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

def get_connection(username, scope):
    """Connect to spotify API. Key/Secrets are passed as environmental variables"""
    token = util.prompt_for_user_token(username, scope)
    client = spotipy.Spotify(auth=token)
    return client

def main():
    client = get_connection(username, scope)
    while True:
        time.sleep(.5)
        res = client.current_user_playing_track()
        with open("check.log", "a") as f: 
            f.write(res.get("item", {}).get("name", {}))
            f.write("\n")
        res = client.next_track()

main()