#!/usr/bin/env python3

import time
import traceback
import json
import sys
from pprint import pprint
import requests
from datetime import datetime, timedelta
import os

import spotipy
import spotipy.util as util

import gi
gi.require_version('Playerctl', '1.0')
from gi.repository import Playerctl, GLib

log_path = '/home/zaibo/data/songs.log'
username = '1253958435'
scope = 'user-read-playback-state'


"""
Notes and useful links for future reference:
- Unsure what GLib is doing. As far as I understand, PlayerCtl is the interface that handles everything for logging

# PlayerCtl methods
https://lazka.github.io/pgi-docs/Playerctl-1.0/mapping.html

# PlayerCtl github page
https://github.com/acrisci/playerctl
with example scripts:
https://github.com/acrisci/playerctl/tree/master/examples

I couldn't get player.connect() to work (used in example) so using player.on() instead

player.props.position should be the track position,
however, this is not supported by Spotify as of 12/31/18

For spotipy, remember to PASTE the URL into terminal (I spent hours trying to debug this
because my reading comprehension was poor)
"""


class PlayerStatus:
    def __init__(self):
        self._player = None

        # Connect to spotify API. Key/Secrets are passed as environmental variables
        token = util.prompt_for_user_token(username, scope)
        self._client = spotipy.Spotify(auth=token)

        # All data for logging
        self._artist = None
        self._title = None
        self._album = None
        self._id = None
        self._length = None
        self._start_time = None
        self._end_time = None
        self._shuffle_state = None
        self._repeat_state = None
        self._play_state = None
        self._start_progress = None
        self._end_by = None

        self._last_ev = None

    def show(self):
        self._init_player()

        # Wait for events
        main = GLib.MainLoop()
        main.run()

    def _init_player(self):
        while True:
            try:
                self._player = Playerctl.Player()
                self._player.on('metadata', self._on_metadata)
                self._player.on('play', self._on_play)
                self._player.on('pause', self._on_pause)
                self._player.on('exit', self._on_exit)
                break

            except Exception as e:
                time.sleep(2)

    def api(self):
        try:
            return self._client.current_playback()
        except SpotifyException as e:
            print("Auth token expired")
            token = util.prompt_for_user_token(username, scope)
            self._client = spotipy.Spotify(auth=token)
            return self._client.current_playback()

    def _reset_state(self):
        self._artist = None
        self._title = None
        self._album = None
        self._id = None
        self._length = None
        self._start_time = None
        self._end_time = None
        self._shuffle_state = None
        self._repeat_state = None
        self._play_state = None
        self._start_progress = None

        self._last_artist = None
        self._last_title = None
        self._last_print = None
        self._last_ev = None

    def print_state(self, s=""):
        obj = {
            "title": self._title,
            "artist": self._artist,
            "album": self._album,
            "id": self._id,
            "length": self._length,
            "start_time": self._start_time,
            "shuffle_state": self._shuffle_state,
            "repeat_state": self._repeat_state,
            "play_state": self._play_state,
            "start_progress": self._start_progress,
            "end_progress": self._end_progress,
        }
        print(s)
        pprint(obj)

    def _on_metadata(self, player, e):
        # Deduplicate metadata by 800ms calls
        now = datetime.now()
        # if self._last_ev:
        #     print(now-self._last_ev, now - self._last_ev <=
        #           timedelta(milliseconds=800))
        if self._last_ev and (now - self._last_ev <= timedelta(milliseconds=1000)):
            return
        self._last_ev = now

        api_data = self.api()
        self._end_progress = api_data['progress_ms']

        # There's some tricky race conditions because the API and player are out of sync
        # Waiting .5s before doing the API call is a naive heuristic to fix this.
        time.sleep(.5)

        api_data = self.api()

        # self.print_state("curr")
        if self._start_time is None:
            # Ignore in case player is alredy playing
            if not api_data['is_playing']:
                return
            # First run of script, must initialize
            print("init")
            self._artist = e['xesam:artist']
            self._album = self._player.get_album()
            self._title = e['xesam:title']
            self._id = e['mpris:trackid']
            self._length = e['mpris:length']
            self._device = api_data.get('device', {}).get('name', '')
            self._shuffle_state = api_data['shuffle_state']
            # self._shuffle_state = api_data.get('shuffle_state', False)
            self._repeat_state = api_data['repeat_state']
            # self._repeat_state = api_data.get('repeat_state', False)
            self._play_state = api_data['is_playing']
            # self._play_state = api_data.get('is_playing', False)
            self._start_progress = self._end_progress
            # self._start_progress = api_data['progress_ms']
            self._start_time = now.isoformat()
        else:
            if api_data['shuffle_state'] != self._shuffle_state:
                # Event was shuffle state change
                # Update the shuffle state
                print("shuffle change", self._shuffle_state,
                      api_data.get('shuffle_state'))
                self._shuffle_state = api_data['shuffle_state']
            elif api_data.get('repeat_state') != self._repeat_state:
                # Event was repeat state change
                # Update the repeat state
                print("repeat state")
                self._repeat_state = api_data.get('repeat_state', False)
            elif self._play_state and not api_data.get('is_playing'):
                # Event was play -> pause
                # Record a log and reset state
                print("paused")
                self._end_by = "pause"
                # self._end_progress = api_data['progress_ms']
                self._print_song()
                self._reset_state()
            elif self._id != e['mpris:trackid']:
                # Event was change to new track
                # Record log for previous track
                # Assume previous track was played from start_time to completion
                # Update state to current song
                print("new song")
                # self._end_progress = api_data['progress_ms']
                self._end_by = "new song"
                self._print_song()

                self._album = self._player.get_album()
                self._artist = e['xesam:artist']
                self._title = e['xesam:title']
                self._id = e['mpris:trackid']
                self._length = e['mpris:length']
                self._device = api_data.get('device', {}).get('name', '')
                self._shuffle_state = api_data['shuffle_state']
                self._repeat_state = api_data['repeat_state']
                self._start_progress = api_data['progress_ms']
                # self._start_progress = self._end_progress
                self._start_time = datetime.now().isoformat()
            elif self._id == e['mpris:trackid']:
                # Event was track was repeated
                # Record log for the track and update time
                print("same song on repeat")
                self._end_by = "same song on repeat"
                # self._end_progress = api_data['progress_ms']
                self._print_song()

                self._artist = e['xesam:artist']
                self._album = self._player.get_album()
                self._title = e['xesam:title']
                self._id = e['mpris:trackid']
                self._length = e['mpris:length']
                self._device = api_data.get('device', {}).get('name', '')
                self._shuffle_state = api_data['shuffle_state']
                self._repeat_state = api_data['repeat_state']
                self._start_progress = api_data['progress_ms']
                # self._start_progress = self._end_progress
                self._start_time = datetime.now().isoformat()
        # self.print_state("new")
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    def _on_play(self, player):
        # self._print_song()
        # print("set play to true")
        # self._play_state = True
        pass

    def _on_pause(self, player):
        # self._print_song()
        # print("set play to false")
        # self._play_state = False
        pass

    def _on_exit(self, player):
        self._init_player()

    def round_progress(self):
        if self._end_progress < 5000:
            self._end_progress = 0
        elif abs(self._end_progress - self._length//1000) < 5000:
            self._end_progress = self_length//1000

        if self._start_progress < 5000:
            self._start_progress = 0
        elif abs(self._start_progress - self._length//1000) < 5000:
            self._start_progress = self_length//1000

    def _print_song(self):
        self.round_progress()
        duration = self._end_progress - self._start_progress
        if duration < 0:
            print("duration less than 0")
            return
        obj = {
            "title": self._title,
            "artist": self._artist,
            "album": self._album,
            "id": self._id,
            "length": int(self._length/1000000),
            "start_time": self._start_time,
            "end_time": datetime.now().isoformat(),
            "shuffle_state": self._shuffle_state,
            "repeat_state": self._repeat_state,
            "play_state": self._play_state,
            "start_progress": self._start_progress,
            "end_progress": self._end_progress,
            "end_by": self._end_by,
            "duration": duration
        }
        s = json.dumps(obj) + '\n'
        # print(s)
        with open(log_path, 'a') as f:
            f.write(s)


# url = 'https://api.spotify.com/v1/me/player'
# token = os.environ['SPOTIFY_AUTH']
# response = requests.get(url,
#                         headers={'Content-Type': 'application/json',
#                                  'Authorization': 'Bearer {}'.format(token)})
# json_data = json.loads(response.text)
# print(json_data)

# url = 'https://accounts.spotify.com/authorize'
# token = os.environ['SPOTIFY_AUTH']
# response = requests.get(url,
#                         headers={'Content-Type': 'application/json',
#                                  'Authorization': 'Bearer {}'.format(token)})
# json_data = json.loads(response.text)
# print(json_data)

# id = '7cb030cf04a240af9eaa49d7d06dcfce'
# redir = 'https://localhost:3000/'
# scope = 'user-read-playback-state'
# auth_url = 'https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri={}&scope={}'.format(
#     id, redir, scope)

# response = requests.get(auth_url, headers={'Content-Type': 'application/json'})
# print(response.text)

PlayerStatus().show()
