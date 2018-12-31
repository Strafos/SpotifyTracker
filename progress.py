
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


token = util.prompt_for_user_token(username, scope)
client = spotipy.Spotify(auth=token)
data = client.current_playback()
print(data["progress_ms"])
