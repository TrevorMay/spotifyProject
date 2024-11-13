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
                                               scope='playlist-read-private playlist-read-collaborative'))


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

# Get current user's playlists
playlists = sp.current_user_playlists()

# Initialize a list to hold all track data
tracks_data = []

# Loop through each playlist
for playlist in playlists['items']:
    playlist_name = playlist['name']
    playlist_id = playlist['id']
    
    # Get all tracks in the playlist
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            track = item['track']
            song_id = track['id']
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            
            tracks_data.append({
                'song_id': song_id,
                'song_name': song_name,
                'artist_name': artist_name,
                'playlist_name': playlist_name
            })
        
        # Pagination - Get next batch of tracks
        results = sp.next(results) if results['next'] else None

# Convert list to DataFrame
df = pd.DataFrame(tracks_data)

# Save to CSV
df.to_csv('spotify_songs.csv', index=False)

print(f"Successfully saved {len(df)} songs to spotify_songs.csv")

# %% [markdown]
# # DATABASE STUFF NOT WORKING

# %%
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('spotify_library.db')
cursor = conn.cursor()

# Create Songs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Songs (
    song_id TEXT PRIMARY KEY,
    title TEXT,
    artist_id TEXT,
    album_id TEXT,
    duration INTEGER,
    popularity INTEGER,
    added_at TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES Artists (artist_id),
    FOREIGN KEY (album_id) REFERENCES Albums (album_id)
)
''')

# Create Artists table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Artists (
    artist_id TEXT PRIMARY KEY,
    name TEXT,
    genres TEXT
)
''')

# Create Albums table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Albums (
    album_id TEXT PRIMARY KEY,
    title TEXT,
    artist_id TEXT,
    release_date DATE,
    total_tracks INTEGER,
    FOREIGN KEY (artist_id) REFERENCES Artists (artist_id)
)
''')

# Create Playlists table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Playlists (
    playlist_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    owner_id TEXT,
    public BOOLEAN
)
''')

# Create Playlist_Songs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Playlist_Songs (
    playlist_id TEXT,
    song_id TEXT,
    added_at TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlists (playlist_id),
    FOREIGN KEY (song_id) REFERENCES Songs (song_id)
)
''')

# Commit and close connection
conn.commit()
# conn.close()

# %%
import time
import datetime

# Function to insert data into the database
def insert_data():
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        playlist_id = playlist['id']
        name = playlist['name']
        if name in playlists_remaining:
            description = playlist['description']
            owner_id = playlist['owner']['id']
            public = playlist['public']
    
            print(f"Inserting playlist: {name}")
            
            cursor.execute('''
                INSERT OR IGNORE INTO Playlists (playlist_id, name, description, owner_id, public)
                VALUES (?, ?, ?, ?, ?)
            ''', (playlist_id, name, description, owner_id, public))
            
            tracks = sp.playlist_tracks(playlist_id)
            for item in tracks['items']:
                track = item['track']
                song_id = track['id']
                title = track['name']
                print(title)
                artist_id = track['artists'][0]['id']
                album_id = track['album']['id']
                duration = track['duration_ms']
                popularity = track['popularity']
                added_at = item['added_at']
                
                cursor.execute('''
                    INSERT OR IGNORE INTO Songs (song_id, title, artist_id, album_id, duration, popularity, added_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (song_id, title, artist_id, album_id, duration, popularity, added_at))
                
                cursor.execute('''
                    INSERT OR IGNORE INTO Playlist_Songs (playlist_id, song_id, added_at)
                    VALUES (?, ?, ?)
                ''', (playlist_id, song_id, added_at))
    
                if artist_id is not None:
                    # artist = sp.artist(artist_id)
                    artist = rate_limited_request(sp.artist, artist_id)
                    time.sleep(0.1)
                    name = artist['name']
                    genres = ', '.join(artist['genres'])
                
                    cursor.execute('''
                        INSERT OR IGNORE INTO Artists (artist_id, name, genres)
                        VALUES (?, ?, ?)
                    ''', (artist_id, name, genres))
    
                if album_id is not None:
                    # album = sp.album(album_id)
                    album = rate_limited_request(sp.album, album_id)
                    time.sleep(0.1)
                    title = album['name']
                    release_date = album['release_date']
                    total_tracks = album['total_tracks']
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO Albums (album_id, title, artist_id, release_date, total_tracks)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (album_id, title, artist_id, release_date, total_tracks))

            conn.commit()
            time.sleep(1)

# Insert data into the database
insert_data()

# Commit and close connection
conn.commit()
conn.close()

# %%
playlists_remaining = [# 'Rainy Days', 
 'Classic Rock / BBQ Music',
 'Desert Road 🏜️ ',
 'Late Nights',
 'Chillin',
 'Nights At The Roxbury',
 "Devil's Lettuce",
 'alt']
