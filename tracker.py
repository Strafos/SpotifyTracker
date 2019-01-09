#!/usr/bin/env python3

import time
import traceback
import json
import sys
from pprint import pprint
import requests
from datetime import datetime, timedelta
import os
import subprocess

import spotipy
import spotipy.util as util
from spotipy.client import SpotifyException

import gi
gi.require_version('Playerctl', '1.0')
from gi.repository import Playerctl, GLib

subprocess.run(
    ["source /home/zaibo/code/spotify-scripts/creds.sh"], shell=True)

log_path = os.environ['SPOTIFY_DATA_PATH']
username = os.environ['SPOTIFY_USERNAME']
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

Issue #1 | 1/08
After testing on server laptop, there's an async issue:
- Player goes to next song
- Playerctl listens to an event
- Script makes a spotify API call, but by this time, it's too late, 
progress is on the next song instead of the end the current song.

Instead of calculating song progress, we can estimate it using duration and start time.

---

Issue #2 | 1/08
Spotify token expires, need new token

We can throw Exception on SpotifyException and restart the script entirely?

---

Using pip gives spotipy 2.0, to upgrade, run 
pip install git+https://github.com/plamere/spotipy.git --upgrade
from https://github.com/plamere/spotipy/issues/337
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
            print("init", datetime.now().isoformat())
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
            self._start_time = now
        else:
            if api_data['shuffle_state'] != self._shuffle_state:
                # Event was shuffle state change
                # Update the shuffle state
                print("shuffle change", datetime.now().isoformat())
                self._shuffle_state = api_data['shuffle_state']
            elif api_data.get('repeat_state') != self._repeat_state:
                # Event was repeat state change
                # Update the repeat state
                print("repeat state", datetime.now().isoformat())
                self._repeat_state = api_data.get('repeat_state', False)
            elif self._play_state and not api_data.get('is_playing'):
                # Event was play -> pause
                # Record a log and reset state
                print("paused", datetime.now().isoformat())
                self._end_by = "pause"
                # self._end_progress = api_data['progress_ms']
                self._print_song()
                self._reset_state()
            elif self._id != e['mpris:trackid']:
                # Event was change to new track
                # Record log for previous track
                # Assume previous track was played from start_time to completion
                # Update state to current song
                print("new song", datetime.now().isoformat())
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
                self._start_time = datetime.now()
            elif self._id == e['mpris:trackid']:
                # Event was track was repeated
                # Record log for the track and update time
                print("same song on repeat", datetime.now().isoformat())
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
                self._start_time = datetime.now()
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

    def round_progress(self, progress):
        """Round progress_ms to song beginning or end if relevant"""
        if progress < 5000:
            return 0
        elif abs(progress - self._length//1000) < 5000:
            return self._length//1000
        else:
            return int(round(progress))

    def _print_song(self):
        # Round start progress
        self._start_progress = self.round_progress(self._start_progress)

        # Get duration in ms using diff in start_time and now
        now = datetime.now()
        duration = int(round((now - self._start_time).total_seconds() * 1000))

        # Round end progress
        end_progress = self.round_progress(self._start_progress + duration)

        # Create log obj
        obj = {
            "title": self._title,
            "artist": self._artist,
            "album": self._album,
            "id": self._id,
            "length": int(self._length/1000),
            "start_time": self._start_time.isoformat(),
            "end_time": now.isoformat(),
            "shuffle_state": self._shuffle_state,
            "repeat_state": self._repeat_state,
            "play_state": self._play_state,
            "start_progress": self._start_progress,
            "end_progress": end_progress,
            "end_by": self._end_by,
            "duration": duration
        }
        s = json.dumps(obj) + '\n'

        # print(s)
        with open(log_path, 'a') as f:
            f.write(s)


PlayerStatus().show()
