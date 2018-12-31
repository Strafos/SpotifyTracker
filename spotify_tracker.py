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


class PlayerStatus:
    def __init__(self):
        self._player = None

        self._artist = None
        self._title = None
        self._id = None
        self._length = None

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
                # self._print_flush('')
                # print("exception")
                print(e)
                time.sleep(2)

    def _on_metadata(self, player, e):
        # pprint(e.keys())
        # pprint(e)
        if 'xesam:artist' in e.keys() and 'xesam:title' in e.keys() and 'mpris:trackid' in e.keys() and 'mpris:length' in e.keys():
            self._artist = e['xesam:artist']
            self._title = e['xesam:title']
            self._id = e['mpris:trackid']
            self._length = e['mpris:length']
            # print(e['xesam:artist'], e['xesam:title'], e['mpris:trackid'],
            #       e['mpris:length'], e['xesam:trackNumber'])

            # self._print_song()

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
            # if self._last_print:
            #     print(now - self._last_print)
            obj = {
                title: self._title,
                artist: self._artist,
                album: self._player.get_album(),
                id: self._id,
                length: self._length,
            }
            s = json.dumps(obj)
            with open(log_path, 'a') as f:
                f.write(curr_song)
            # curr_song = '{}|{}|{}|{}|{}\n'.format(
            #     self._title, self._artist, self._id, self._length, self._player.get_album())
            print(curr_song)
            self._last_print = now
            # traceback.print_stack(file=sys.stdout)

        return


PlayerStatus().show()
