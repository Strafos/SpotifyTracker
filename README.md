# Spotify Tracker

## Dependencies

[spotipy](https://github.com/plamere/spotipy)
[PlayerCtl](https://github.com/acrisci/playerctl)

## tracker

Records comprehensive log of tracks played, including metadata and duration

Example log:

```json
{
  "title": "Worthy",
  "artist": ["Jacob Banks"],
  "album": "Worthy",
  "id": "spotify:track:5vLJqVuOVV5q5ztXJdjxiV",
  "length": 198000,
  "start_time": "2019-01-09T01:56:07.486936",
  "end_time": "2019-01-09T01:59:26.483453",
  "shuffle_state": false,
  "repeat_state": "context",
  "play_state": true,
  "start_progress": 0,
  "end_progress": 198000,
  "end_by": "new song",
  "duration": 198997
}
{
  "title": "Twistin' the Night Away",
  "artist": [
    "Sam Cooke"
  ],
  "album": "The Man Who Invented Soul",
  "id": "spotify:track:6ys9oyFvw7FXbs5UMZ7I7s",
  "length": 160000,
  "start_time": "2019-01-09T01:59:26.483925",
  "end_time": "2019-01-09T02:02:06.904535",
  "shuffle_state": false,
  "repeat_state": "context",
  "play_state": true,
  "start_progress": 0,
  "end_progress": 160000,
  "end_by": "new song",
  "duration": 160421
}
{
  "title": "(What A) Wonderful World",
  "artist": [
    "Sam Cooke"
  ],
  "album": "The Man Who Invented Soul",
  "id": "spotify:track:2g2GkH3vZHk4lWzBjgQ6nY",
  "length": 125000,
  "start_time": "2019-01-09T02:02:06.905650",
  "end_time": "2019-01-09T02:04:12.887997",
  "shuffle_state": false,
  "repeat_state": "context",
  "play_state": true,
  "start_progress": 0,
  "end_progress": 125000,
  "end_by": "new song",
  "duration": 125982
}
```
