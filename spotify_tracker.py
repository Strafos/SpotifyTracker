#!/usr/bin/env python3

import time
import sys
import traceback
from datetime import datetime, timedelta


import gi
gi.require_version('Playerctl', '1.0')
from gi.repository import Playerctl, GLib

MUSIC_ICON = ''
PAUSE_ICON = ''


class PlayerStatus:
    def __init__(self):
        self._player = None
        self._icon = PAUSE_ICON

        self._last_artist = None
        self._last_title = None

        self._last_status = ''
        self._prev_song = ''
        self._last_print = None

    def show(self):
        self._init_player()

        # Wait for events
        main = GLib.MainLoop()
        main.run()

    def _init_player(self):
        while True:
            try:
                print("happens")
                self._player = Playerctl.Player()
                self._player.on('metadata', self._on_metadata)
                self._player.on('play', self._on_play)
                self._player.on('pause', self._on_pause)
                self._player.on('exit', self._on_exit)
                break

            except:
                self._print_flush('')
                time.sleep(2)

    def _on_metadata(self, player, e):
        print(e.keys())
        if 'xesam:artist' in e.keys() and 'xesam:title' in e.keys():
            self._artist = e['xesam:artist'][0]
            self._title = e['xesam:title']

            self._print_song()

    def _on_play(self, player):
        self._print_song()

    def _on_pause(self, player):
        self._print_song()

    def _on_exit(self, player):
        self._init_player()

    def _print_song(self):
        now = datetime.now()
        if self._last_print is None or (now - self._last_print > timedelta(milliseconds=800)):
            # print("first print", self._last_print is None)
            # if self._last_print:
                # print("delta in prints", now - self._last_print)
                # print("100ms", timedelta(milliseconds=100))
                # print("delta in ms", (now - self._last_print).total_microseconds())
                # print("GE 100ms", now - self._last_print >
                #       timedelta(milliseconds=100))
            curr_song = '{} - {}\n'.format(self._artist, self._title)
            print(curr_song)
            self._last_print = now
        # traceback.print_stack(file=sys.stdout)
        # with open('/home/zaibo/code/spotify_analysis/songs.log', 'a') as f:
        #     if curr_song != self._prev_song:
        #         f.write(curr_song)
        #     self._prev_song = curr_song
        return


PlayerStatus().show()
