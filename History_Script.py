import os
import datetime
import pandas as pd
import time
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy

# Load variables from .env file into the environment
load_dotenv()

# Access the environment variables
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
CSV_FILE = 'listening_history.csv'

user_id = os.getenv("USER_ID")

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='user-read-recently-played'))

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='user-read-recently-played'
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

REFRESH_TOKEN = token_info['refresh_token']

sp = spotipy.Spotify(auth_manager=HeadlessSpotifyAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    refresh_token=REFRESH_TOKEN,
    scope='user-read-recently-played'
))


# === DOWNLOAD FUNCTION ===
def fetch_and_append_recent_history():
    print(f"Fetching history at {datetime.datetime.now()}...")
    results = sp.current_user_recently_played(limit=50)
    new_data = []

    for item in results['items']:
        track = item['track']
        played_at = item['played_at']
        new_data.append({
            'played_at': played_at,
            'track_name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'track_id': track['id']
        })

    # Convert to DataFrame
    df_new = pd.DataFrame(new_data)

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=['played_at'], inplace=True)
    else:
        df_combined = df_new

    df_combined.sort_values(by='played_at', inplace=True)
    df_combined.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(df_new)} new records.")


fetch_and_append_recent_history()