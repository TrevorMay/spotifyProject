# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import spotipy
import pyodbc
import time
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# Access the environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

# Replace 'your_user_id' with your actual Spotify user ID
user_id = os.getenv("USER_ID")

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-modify-private'))

# %%
import os

# Remove the cached token file
if os.path.exists('.cache'):
    os.remove('.cache')


# %%
def rate_limited_request(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise


# %%
import pandas as pd

all_songs = pd.read_csv('spotify_songs.csv')
non_TLT_songs = all_songs[~all_songs['playlist_name'].str.contains('TLT')]
non_TLT_songs.head()

# %%
non_TLT_song_ids = set(non_TLT_songs['song_id'])


# %%
def get_playlist_tracks(playlist_id):
    tracks = []
    results = rate_limited_request(sp.playlist_tracks, playlist_id)
    
    while results:
        for item in results.get('items', []):
            track = item.get('track')
            if track:
                tracks.append(track['id'])
        results = rate_limited_request(sp.next, results) if results.get('next') else None
    
    return tracks


# %%
playlists = sp.current_user_playlists()
for playlist in playlists['items']:
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    if 'TLT' in playlist_name: # if it's a to listen to
        tracks = get_playlist_tracks(playlist_id)
        for track in tracks: # go track by track and make sure the songs aren't already in my library
            track_id = track
            if track_id in non_TLT_song_ids:
                sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
                print(f"Track {track_id} has been removed from the playlist {playlist_id}.")
