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
                                               scope='playlist-read-private playlist-modify-private playlist-modify-public'))

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
# # Get user ID
# user_id = sp.current_user()['id']

# # Replace with your playlist name
# playlist_name = "Other TLT"

# # Find the playlist ID
# playlists = sp.user_playlists(user_id)
# playlist_id = None

# for playlist in playlists['items']:
#     if playlist['name'] == playlist_name:
#         playlist_id = playlist['id']

# if not playlist_id:
#     print(f"Playlist '{playlist_name}' not found.")
#     exit()

# # Get tracks from the playlist
# tracks = []
# results = sp.playlist_tracks(playlist_id)
# tracks.extend(results['items'])

# while results['next']:
#     results = sp.next(results)
#     tracks.extend(results['items'])

# # Genre categories and mapping
# genre_categories = {
#     'Electronic': ['electronic', 'edm', 'house', 'techno', 'trance', 'dubstep'],
#     'Pop': ['pop', 'dance pop', 'electropop', 'indie pop', 'synthpop'],
#     'Rock': ['rock', 'alternative rock', 'classic rock', 'indie rock', 'punk'],
#     'R&B': ['r&b', 'soul', 'funk', 'neo-soul'],
#     'Rap': ['rap', 'hip hop', 'trap', 'gangsta rap'],
#     'Classical': ['classical', 'orchestral', 'baroque', 'romantic', 'opera'],
#     'Country': ['country', 'alt-country', 'bluegrass', 'folk'],
#     'Other': []
# }

# # Dictionary to store genre categories and track URIs
# category_tracks = {category: [] for category in genre_categories}

# # Analyze each track and sort by genre categories
# for item in tracks:
#     track = item['track']
#     track_id = track['id']

#     # Get artist's genre information
#     artist_id = track['artists'][0]['id']
#     artist = sp.artist(artist_id)
#     genres = artist['genres']
#     print(genres)

#     if not genres:
#         genres = ['Unknown']

#     categorized = False
#     for genre in genres:
#         genre_lower = genre.lower()
#         for category, keywords in genre_categories.items():
#             if any(keyword in genre_lower for keyword in keywords):
#                 category_tracks[category].append(track['uri'])
#                 categorized = True
#                 break
#         if categorized:
#             break

#     if not categorized:
#         category_tracks['Other'].append(track['uri'])

# # Create or update playlists and add tracks by genre category
# for category, track_uris in category_tracks.items():
#     if track_uris:
#         genre_playlist_name = f"{category.capitalize()} Songs"
#         # Check if playlist already exists
#         existing_playlist = None
#         for playlist in playlists['items']:
#             if playlist['name'] == genre_playlist_name:
#                 existing_playlist = playlist
#                 break

#         if existing_playlist:
#             playlist_id = existing_playlist['id']
#             # sp.user_playlist_replace_tracks(user_id, playlist_id, track_uris)
#             print(f"Updated playlist '{genre_playlist_name}' with {len(track_uris)} tracks.")
#         else:
#             genre_playlist = sp.user_playlist_create(user_id, genre_playlist_name)
#             # sp.user_playlist_add_tracks(user_id, genre_playlist['id'], track_uris)
#             print(f"Created playlist '{genre_playlist_name}' with {len(track_uris)} tracks.")

# print("Done!")

# %%
# Get user ID
user_id = sp.current_user()['id']

# Replace with your playlist name
playlist_name = "Other TLT"

# Find the playlist ID
playlists = sp.user_playlists(user_id)
print('made it past playlists request')
playlist_id = None

for playlist in playlists['items']:
    print(playlist['name'])
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        break

if not playlist_id:
    print(f"Playlist '{playlist_name}' not found.")
    exit()

# Get tracks from the playlist
tracks = []
results = sp.playlist_tracks(playlist_id)
tracks.extend(results['items'])
print('made it past tracks request')

while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

print('made it past results')

# Dictionary to store genres and track URIs
genre_tracks = {}

# Analyze each track and sort by genre
for item in tracks:
    track = item['track']
    track_id = track['id']
    print(track['name'])

    # Get audio features and genre information
    artist_id = str(track['artists'][0]['id'])
    if artist_id != '7guDJrEfX3qb6FEbdPA5qi':
        print(artist_id)
        artist = sp.artist(artist_id)
        print(artist)
        genres = artist['genres']

        if not genres:
            genres = ['Unknown']
    
        for genre in genres:
            if genre not in genre_tracks:
                genre_tracks[genre] = []
            genre_tracks[genre].append(track['uri'])

# Create new playlists and add tracks by genre
for genre, track_uris in genre_tracks.items():
    genre_playlist_name = f"{genre.capitalize()} Songs"
    # genre_playlist = sp.user_playlist_create(user_id, genre_playlist_name)
    # sp.user_playlist_add_tracks(user_id, genre_playlist['id'], track_uris)

    print(f"Created playlist '{genre_playlist_name}' with {len(track_uris)} tracks.")

print("Done!")
