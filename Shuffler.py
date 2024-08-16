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
# # !pip install spotipy
# # !pip install jupytext
# # !pip install pandas
import sys

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
# Fetch the current user's playlists
playlists = sp.current_user_playlists()

# Display the playlists and their IDs
for playlist in playlists['items']:
    print(f"Name: {playlist['name']}, ID: {playlist['id']}")

print("All playlists fetched successfully!")

# %%
PLAYLIST_DICT = {
    '2tciVu41abGNGGDTor8ymi': 'Pop jams',
    '02amPkup87qzafM74GaBio': 'Country',
    '4lljfJpe1l0IIHghRghBtw': 'Skux Life',
    '5PocUkbg0I7wy9qBpJkehp': 'Rap',
    '1R6uRy98QBq8fmq7KY1loJ': 'Classic Chill Rap',
    '4EvCXZDLdnJfAYUUqAeFp4': 'R&B',
    '4I93rJXYxrwMOgOrueztzt': 'White Noise Ambient',
    '5artPRbCYgZHoWmkaS1Qwo': 'New R&B',
    '3s7zMU3AEY6clhnHXl54Cq': 'Rock - Retirement',
    '5PBj2MCDvGlmxFFJJMyDDl': 'Country - Retirement',
    '6jZlLmmY9Brko7ohKPIghE': 'EDM - Retirement',
    '1vRyUUQuoK1bgERMI15bZM': 'Rap - Retirement',
    '4Dn82KRwRl79HwCibPCg3g': 'Baby Driver',
    '4InvgPgwdpYWdxDvTAGXx6': 'Meditation Music',
    '0mXPvAzrlEBUfshpde5Xll': 'Relaxing Baby Music',
    '2ng5uPHZ44mCTRfmCqMQl2': 'Work Jams',
    '48xx6foIN9FRJAAIBnrnFo': 'Full Focus',
    '0HhSRNnQX0UctzwaDPoRnz': 'Shower Karaoke',
    '7xULdcgCdm4QM4D4OJQqgj': 'Gym',
    '2R0mnMr78Nku1v6PwRsjBW': 'Holiday Tunes',
    '7iyW4cHp6CvMRwBpt4b7Pr': 'Spooky Tunes',
    '2g9mZeeETYX5YPvnsccSIT': '.think',
    '5RAagXBkK2HpyKVX4ZuNkJ': 'It\'s a good day',
    '6aFoEzi4P7xma7TuzyXlud': 'Summer Jams',
    '2UMzHLkmlkVfCjMeZWE1Ss': 'Rainy Days',
    '5iL9YJwiEil0ebEzCmACXg': 'Classic Rock / BBQ Music',
    '25Cz82cEBT50PxqprN5B1a': 'Desert Road',
    '6lpW8iDy95jCWX976Ujr7P': 'Late Nights',
    '5MxlRcAT7NS0YZAbkHwTrZ': 'Chillin',
    '1eZrPoXiEaIs1ZVDgx9JQM': 'Nights At the Roxbury',
    '1AMZ0uS8KoxPRPqGHuzGhE': 'Devil\'s Lettuce',
    '4uxk9ZYpyL4Uqxw9jTKm82': 'alt',
    '44okKoHjUXErp3wXowRUDx': '2000s bops',
    '3n6jvXn4Av8h6p9l5HolIO': '90s // Classic R&B',
    '4dCrVJEWn25z1tnEDpcfTs': '50s / 60s'
}


# %%
PLAYLIST_IDS = ['2tciVu41abGNGGDTor8ymi', # Pop jams
                '02amPkup87qzafM74GaBio', # Country
                '4lljfJpe1l0IIHghRghBtw', # Skux Life
                '5PocUkbg0I7wy9qBpJkehp', # Rap
                '1R6uRy98QBq8fmq7KY1loJ', # Classic Chill Rap
                '4EvCXZDLdnJfAYUUqAeFp4', # R&B
                '4I93rJXYxrwMOgOrueztzt', # White Noise Ambient
                '5artPRbCYgZHoWmkaS1Qwo', # New R&B
                '4Dn82KRwRl79HwCibPCg3g', # Baby Driver
                '4InvgPgwdpYWdxDvTAGXx6', # Meditation Music
                '0mXPvAzrlEBUfshpde5Xll', # Relaxing Baby Music
                '2ng5uPHZ44mCTRfmCqMQl2', # Work Jams
                '48xx6foIN9FRJAAIBnrnFo', # Full Focus
                '0HhSRNnQX0UctzwaDPoRnz', # Shower Karaoke
                '7xULdcgCdm4QM4D4OJQqgj', # Gym
                '2R0mnMr78Nku1v6PwRsjBW', # Holiday Tunes
                '7iyW4cHp6CvMRwBpt4b7Pr', # Spooky Tunes
                '2g9mZeeETYX5YPvnsccSIT', # .think
                '5RAagXBkK2HpyKVX4ZuNkJ', # It's a good day
                '6aFoEzi4P7xma7TuzyXlud', # Summer Jams
                '2UMzHLkmlkVfCjMeZWE1Ss', # Rainy Days
                '5iL9YJwiEil0ebEzCmACXg', # Classic Rock / BBQ Music
                '25Cz82cEBT50PxqprN5B1a', # Desert Road
                '6lpW8iDy95jCWX976Ujr7P', # Late Nights
                '5MxlRcAT7NS0YZAbkHwTrZ', # Chillin
                '1eZrPoXiEaIs1ZVDgx9JQM', # Nights At the roxbury
                '1AMZ0uS8KoxPRPqGHuzGhE', # Devil's Lettuce
                '4uxk9ZYpyL4Uqxw9jTKm82', # alt
                '44okKoHjUXErp3wXowRUDx', # 2000s bops
                '3n6jvXn4Av8h6p9l5HolIO', # 90s // Classic R&B 
                '4dCrVJEWn25z1tnEDpcfTs'] # 50s / 60s
                

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

# def fetch_all_tracks_from_playlist(playlist_id):
#     tracks = []
#     results = rate_limited_request(sp.playlist_tracks, playlist_id)
#     if results['next'] and len(results['items']) > 0: # if playlist is not empty
#         try:
#             tracks.extend(results['track']['id'])
#         except Exception as e:
#             print(e)
#             print('---------------------------------------------------------------------------------------')
#             print(results)
#             sys.exit()
#     while results['next'] and len(results['items']) > 0:
#         results = rate_limited_request(sp.next, results)
#         tracks.extend(results['track']['id'])
    
#     return list(tracks)

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
                
for PLAYLIST_ID in PLAYLIST_IDS:
    # Fetch all the tracks from the playlist
    tracks = get_playlist_tracks(PLAYLIST_ID)
    
    # Shuffle the tracks
    random.shuffle(tracks)
    
    # Clear the current playlist
    rate_limited_request(sp.playlist_replace_items, PLAYLIST_ID, [])
    
    # Add the shuffled tracks to the playlist in chunks of 100
    for i in range(0, len(tracks), 100):
        rate_limited_request(sp.playlist_add_items, PLAYLIST_ID, tracks[i:i + 100])
    
    print(f"{PLAYLIST_DICT[PLAYLIST_ID]} shuffled successfully!")

print('------------------------------------------------------------')
print('ALL DONE!')

