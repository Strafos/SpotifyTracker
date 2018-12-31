#!/usr/bin/env python3

import time
import traceback
import json
import sys
from pprint import pprint
from datetime import datetime, timedelta

import gi
gi.require_version('Playerctl', '1.0')
from gi.repository import Playerctl, GLib

log_path = '/home/zaibo/code/spotify_analysis/songs.log'

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
"""


class PlayerStatus:
    def __init__(self):
        self._player = None

        self._artist = None
        self._title = None
        self._id = None
        self._length = None
        self._start_time = None

        self._last_artist = None
        self._last_title = None
        self._last_print = None

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

    def _on_metadata(self, player, e):
        if 'xesam:artist' in e.keys() and 'xesam:title' in e.keys() and 'mpris:trackid' in e.keys() and 'mpris:length' in e.keys():
            self._artist = e['xesam:artist']
            self._title = e['xesam:title']
            self._id = e['mpris:trackid']
            self._length = e['mpris:length']

    def _on_play(self, player):
        self._print_song()

    def _on_pause(self, player):
        # self._print_song()
        pass

    def _on_exit(self, player):
        self._init_player()

    def _print_song(self):
        now = datetime.now()

        if self._last_print is None or (now - self._last_print > timedelta(milliseconds=800)):
            obj = {
                "title": self._title,
                "artist": self._artist,
                "album": self._player.get_album(),
                "id": self._id,
                "length": int(self._length/1000000),
                "time": now.isoformat()
            }
            s = json.dumps(obj) + '\n'
            # print(s)
            with open(log_path, 'a') as f:
                f.write(s)
            self._last_print = now
            # traceback.print_stack(file=sys.stdout)


PlayerStatus().show()
