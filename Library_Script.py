import sys
import spotipy
import time
import os
import random
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException

# Load variables from .env file into the environment
load_dotenv()

# Access the environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
user_id = os.getenv("USER_ID")

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-read-private playlist-modify-private playlist-modify-public'))

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='playlist-read-private playlist-modify-private playlist-modify-public'
)


token_info = sp_oauth.get_cached_token()
if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(f"Go to this URL to authorize: {auth_url}")
    response = input("Paste the URL you were redirected to: ")

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

class HeadlessSpotifyAuth(SpotifyOAuth):
    def __init__(self, refresh_token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refresh_token_value = refresh_token

    def get_access_token(self, code=None, as_dict=True, check_cache=True):
        token_info = self.refresh_access_token(self.refresh_token_value)
        return token_info if as_dict else token_info['access_token']

# Replace with your actual values
REFRESH_TOKEN = token_info['refresh_token']

sp = spotipy.Spotify(auth_manager=HeadlessSpotifyAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    refresh_token=REFRESH_TOKEN,
    scope='playlist-read-private'
))

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