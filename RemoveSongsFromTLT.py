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
import random
import pyodbc
import requests
import time
import base64
import os
import pandas as pd
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
                                               scope='playlist-read-private playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public'))

# %%
import os

# Remove the cached token file
if os.path.exists('.cache'):
    os.remove('.cache')


# %%
def get_access_token(client_id, client_secret):
    # Set the Spotify API token endpoint
    token_url = r"https://accounts.spotify.com/api/token"
    # Encode the client ID and client secret to base64
    auth_str = f"{client_id}:{client_secret}"
    
    encoded_auth_str = base64.b64encode(auth_str.encode()).decode('utf-8')

    # Headers for the POST request
    headers = {
        'Authorization': f'Basic {encoded_auth_str}'
    }

    # Parameters for the POST request
    params = {
        'grant_type': 'client_credentials'
    }

    # Make the POST request to get the access token
    response = requests.post(token_url, data=params, headers=headers)

    if response.status_code == 200:
        # Access token obtained successfully
        access_token = response.json().get('access_token')
        return access_token
    else:
        print(f"Error: Unable to get access token. Status code: {response.status_code}")
        return None

access_token = get_access_token(client_id, client_secret)
if access_token:
    print(f"Access token: {access_token}")
else:
    print("Failed to obtain access token.")

# %%
# def rate_limited_request(func, *args, **kwargs):
#     while True:
#         try:
#             return func(*args, **kwargs)
#         except spotipy.exceptions.SpotifyException as e:
#             if e.http_status == 429:
#                 retry_after = int(e.headers.get("Retry-After", 1))
#                 print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
#                 time.sleep(retry_after)
#             else:
#                 raise

# %%
import time
import random
from spotipy.exceptions import SpotifyException

# Improved rate-limited request function with retry limits to prevent infinite loops
def rate_limited_request(func, *args, max_retries=5, **kwargs):
    retries = 0  # Initialize retry counter
    while retries < max_retries:
        try:
            return func(*args, **kwargs)  # Attempt to execute the function
        except SpotifyException as e:
            if e.http_status == 429:  # Check if the error is due to rate limiting
                # Get the suggested retry-after time, with a random additional delay
                retry_after = int(e.headers.get("Retry-After", 1))
                retry_after = retry_after + random.randint(1, 10)
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds... (Attempt {retries + 1} of {max_retries})")
                time.sleep(retry_after)  # Wait before retrying
                retries += 1  # Increment the retry counter
            else:
                # Handle other Spotify exceptions and exit the retry loop
                print(f"SpotifyException encountered: {e}")
                break
        except Exception as e:
            # Handle any other unexpected exceptions and exit the retry loop
            print(f"Unexpected error: {e}")
            break

    print(f"Max retries reached for {func.__name__}. Unable to complete request.")
    return None  # Return None if max retries are reached


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
                print(f"Track {track_id} has been removed from the playlist {playlist_name}.")

# %%
tracks = get_playlist_tracks('5P36gcPJgStoWudUwX0ZCC')
tracks
