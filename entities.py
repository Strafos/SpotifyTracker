class Track():
    def __init__(self, item):
        self.name = item.get('track', {}).get('name', "")
        self.uri = item.get('track', {}).get('uri', "")
        self.id = item.get('track', {}).get('id', "")
        self.artists = [Artist(artist) for artist in item.get('track', {}).get('artists', [])]

class Artist():
    def __init__(self, artist):
        self.name = artist['name']
        self.id = artist['id']
        self.uri = artist['uri']

class Playlist():
    def __init__(self, songs):
        self.songs = songs