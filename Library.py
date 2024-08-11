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

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-read-private'))


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
import time
import datetime

# Function to insert data into the database
def insert_data():
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        playlist_id = playlist['id']
        name = playlist['name']
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

            time.sleep(1)

# Insert data into the database
insert_data()

# Commit and close connection
conn.commit()
conn.close()
