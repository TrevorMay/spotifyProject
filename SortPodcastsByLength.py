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
                                               scope='user-library-read playlist-modify-private'))

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
# Initialize a list to hold all episode data
episodes_data = []

# Get episodes from "Your Episodes" (saved episodes)
results = sp.current_user_saved_episodes()

while results:
    for item in results['items']:
        episode = item['episode']
        episode_id = episode['id']
        episode_name = episode['name']
        show_name = episode['show']['name']
        duration_ms = episode['duration_ms']  # Duration in milliseconds
        
        episodes_data.append({
            'episode_name': episode_name,
            'show_name': show_name,
            'duration_ms': duration_ms,
            'episode_id': episode_id
        })
    
    # Pagination - Get next batch of episodes
    results = sp.next(results) if results['next'] else None

# Convert list to DataFrame
df = pd.DataFrame(episodes_data)

# Sort the episodes by duration (longest to shortest)
df_sorted = df.sort_values(by='duration_ms', ascending=False)

# %%
df_sorted

# %%
# Create a new playlist named "Episodes Sorted By Length"
user_id = sp.current_user()['id']
playlist_name = 'Episodes Sorted By Length'
playlist_description = 'A playlist of my saved podcast episodes sorted by length from longest to shortest.'

new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=playlist_description)
playlist_id = new_playlist['id']

# Add sorted episodes to the new playlist in chunks of 100
episode_ids = df_sorted['episode_id'].tolist()
chunk_size = 20

for i in range(0, len(episode_ids), chunk_size):
    sp.playlist_add_items(playlist_id, episode_ids[i:i+chunk_size])

print(f"Added {len(episode_ids)} episodes to the playlist '{playlist_name}'.")
