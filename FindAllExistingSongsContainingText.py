# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
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
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Replace 'your_user_id' with your actual Spotify user ID
user_id = os.getenv("USER_ID")

# %%
# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-library-read playlist-modify-public playlist-modify-private playlist-read-private"))


# %%
# Function to search for all tracks containing the text 'coming home'
def get_all_tracks(query, limit=50, max_offset=1000):
    track_uris = []
    offset = 0
    while offset < max_offset:
        results = sp.search(q=query, type='track', limit=limit, offset=offset)
        if results is None:
            print("No results returned, exiting loop.")
            break
        tracks = results.get('tracks', {}).get('items', [])
        if not tracks:
            print("No more tracks found, exiting loop.")
            break
        track_uris.extend([track['uri'] for track in tracks])
        offset += limit
        print(f"Fetched {len(tracks)} tracks, total so far: {len(track_uris)}")
    return track_uris

# Search for tracks containing the text 'coming home'
query = 'home'
track_uris = get_all_tracks(query)

# Create a new playlist
playlist_name = 'Coming Home Songs'
playlist_description = 'A playlist of songs containing "coming home"'
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

# Add tracks to the new playlist in batches (maximum of 100 tracks per request)
for i in range(0, len(track_uris), 100):
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris[i:i+100])

print(f'Added {len(track_uris)} songs to the playlist "{playlist_name}".')

