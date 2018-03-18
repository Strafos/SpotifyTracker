class Track():
    def __init__(self, item):
        self.name = item['track']['name']
        self.uri = item['track']['uri']
        self.id = item['track']['id']
        self.artists = [Artist(artist) for artist in item['track']['artists']]

class Artist():
    def __init__(self, artist):
        self.name = artist['name']
        self.id = artist['id']
        self.uri = artist['uri']

class Playlist():
    def __init__(self, songs):
        self.songs = songs