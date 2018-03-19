# Spotify Scripts

There are some features I want that Spotify doesn't have. In general, I want to be able to write scripts that describe exactly what I want to listen to. This is done using Spotify's API and python wrapper, spotipy

## Dependencies
[spotipy](https://github.com/plamere/spotipy)

## special_shuffle
Shuffle playlist by artists that have at least 10 songs in the playlist. Creates a queue of 100 songs, so after running the script, I can use the Spotify client to skip songs, repeat, etc.