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
                                               scope='playlist-read-private playlist-modify-private playlist-modify-public', requests_timeout=10))

# %%
# Remove the cached token file
if os.path.exists('.cache'):
    os.remove('.cache')

# %%
# def rate_limited_request(func, *args, **kwargs):
#     while True:
#         try:
#             return func(*args, **kwargs)
#         except spotipy.exceptions.SpotifyException as e:
#             if e.http_status == 429:
#                 retry_after = int(e.headers.get("Retry-After", 1))
#                 retry_after = retry_after + random.randint(1, 10)
#                 print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
#                 time.sleep(retry_after)
#             else:
#                 print(e)
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
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

# Function to get tracks from a playlist
def get_tracks_from_playlist(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Example function to extract features in batch (you'll need to implement this to suit your setup)
def extract_features_batch(track_ids):
    # Assuming this function uses Spotify's `audio_features` endpoint to get features in bulk
    # Replace with your actual API call logic
    features = rate_limited_request(sp.audio_features, track_ids)  # Modify this to match your API setup
    return features


# %%
# Fetch tracks from your playlists and create a labeled dataset
playlists = {
    '5P36gcPJgStoWudUwX0ZCC': 'pop',  
    '6OsJ4cmdvodbqHKHO4fUNg': 'rock',
    '1d6b5iJk8QjWEs6FrR1JPI': 'electronic',
    '6s7uiLkGuV19avNRwdWIIj': 'r_and_b',
    '2pKInR4KBvpIbp28FWm3tE': 'indie',
    '4Om6SVyGS7C7M4i0gyds0E': 'jazz',
    '6McmjBuxieguU5zxCy98r8': 'classical',
    '6jRyO0OAe3JUYv92YrNLFq': 'rap'
}

# %%
data = []
labels = []

# Loop through playlists
for playlist_id, genre in playlists.items():
    print('----------------------------------------------------')
    print(f'Now getting features for genre: {genre}')
    tracks = get_tracks_from_playlist(playlist_id)

    # Extract track IDs and names from tracks
    track_ids = [track['track']['id'] for track in tracks]
    track_names = [track['track']['name'] for track in tracks]

    # Process tracks in batches of 100
    for i in range(0, len(track_ids), 100):
        batch_ids = track_ids[i:i + 100]
        batch_names = track_names[i:i + 100]
        print(f'Now getting features for batch: {i}-{i + 100}')

        try:
            # Get features for the batch of 100 tracks
            features_batch = extract_features_batch(batch_ids)
            for features, name in zip(features_batch, batch_names):
                if features:  # Check if features are not None
                    # Extract only the desired numerical features
                    numerical_features = [
                        features['danceability'],
                        features['energy'],
                        features['speechiness'],
                        features['acousticness'],
                        features['instrumentalness'],
                        features['liveness'],
                        features['valence'],
                        features['tempo'],
                    ]
                    data.append(numerical_features)
                    labels.append(genre)
                else:
                    print(f"Features not found for song: {name}")
        except Exception as e:
            print(f"Error extracting features for batch {i}-{i + 100}: {e}")

# Convert to DataFrame
df = pd.DataFrame(data, columns=['danceability', 'energy', 'speechiness', 'acousticness', 
                                 'instrumentalness', 'liveness', 'valence', 'tempo'])
df['genre'] = labels

# Encode genres as numerical values
label_encoder = LabelEncoder()
df['genre'] = label_encoder.fit_transform(df['genre'])

# Get the mapping of original labels to encoded values
label_mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
reverse_mapping = dict(zip(range(len(label_encoder.classes_)), label_encoder.classes_))

print("Label Mapping:", label_mapping)        # Original label -> Encoded value
print("Reverse Mapping:", reverse_mapping)    # Encoded value -> Original label

# Save DataFrame to CSV
df.to_csv('TLT_genres.csv', index=False)

# %%
df = pd.read_csv('TLT_genres.csv')

# %%
# Train-test split
X = df.drop('genre', axis=1)
y = df['genre']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train, y_train)

# Evaluate the model
y_pred = classifier.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# %%
import pandas as pd

df = pd.read_csv('TLT_genres.csv')
df.head()

# %%
df['genre'] = labels

# Encode genres as numerical values
label_encoder = LabelEncoder()
df['genre'] = label_encoder.fit_transform(df['genre'])

# Get the mapping of original labels to encoded values
label_mapping = dict(zip(label_encoder.classes_, range(len(label_encoder.classes_))))
reverse_mapping = dict(zip(range(len(label_encoder.classes_)), label_encoder.classes_))

print("Label Mapping:", label_mapping)        # Original label -> Encoded value
print("Reverse Mapping:", reverse_mapping)    # Encoded value -> Original label

# %%
print("Label Mapping:", label_mapping)        # Original label -> Encoded value
print("Reverse Mapping:", reverse_mapping)    # Encoded value -> Original label


# %%
def get_playlist_tracks(playlist_id):
    tracks = []
    results = rate_limited_request(sp.playlist_tracks, playlist_id)
    
    while results:
        for item in results.get('items', []):
            tracks.append(item)
        results = rate_limited_request(sp.next, results) if results.get('next') else None
    
    return tracks


# %%
source_playlist_id = '6fbYFsJU3Fz6uIkooJvIbq'

# Define your genre-specific playlists with their Spotify IDs
genre_playlists = {
    'rock': '6OsJ4cmdvodbqHKHO4fUNg',  
    'classical': '6McmjBuxieguU5zxCy98r8',
    'pop': '5P36gcPJgStoWudUwX0ZCC',
    'jazz': 'JAZZ_PLAYLIST_ID',
    'country': '6s7uiLkGuV19avNRwdWIIj',
    'r_and_b': '6hEJKk2mF1uBG50G6bsmbF',
    'electronic': '1d6b5iJk8QjWEs6FrR1JPI',
    'rap': '6jRyO0OAe3JUYv92YrNLFq',
}

# Function to extract features for a batch of track IDs
def extract_features_batch(track_ids):
    features_batch = rate_limited_request(sp.audio_features, track_ids)
    features_list = []
    for features in features_batch:
        if features:  # Ensure features are not None
            features_list.append([
                features['danceability'],
                features['energy'],
                features['speechiness'],
                features['acousticness'],
                features['instrumentalness'],
                features['liveness'],
                features['valence'],
                features['tempo']
            ])
        else:
            features_list.append([None] * 8)  # Handle missing features
    return features_list

# Function to move songs based on genre prediction
def move_songs_to_genre_playlists(source_playlist_id):
    # Get tracks from the source playlist
    tracks = get_playlist_tracks(source_playlist_id)
    
    # Collect track IDs and metadata
    track_ids = []
    track_info = []  # Store track name and artist for debugging or logging
    
    for track in tracks:
        track_id = track['track']['id']
        track_name = track['track']['name']
        track_artist = track['track']['artists'][0]['name']
        
        track_ids.append(track_id)
        track_info.append((track_name, track_artist))
        
        # Process in batches of 100
        if len(track_ids) == 100 or track == tracks[-1]:
            features_batch = extract_features_batch(track_ids)
            
            # Filter out rows with None values
            features_batch = [f for f in features_batch if None not in f]
            
            # Convert features to a DataFrame
            features_df = pd.DataFrame(features_batch, columns=[
                'danceability', 'energy', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'tempo'
            ])
            
            # Predict genres
            predictions = classifier.predict(features_df)
            
            # Move songs to respective genre-specific playlists
            for idx, genre in enumerate(predictions):
                genre_playlist_id = genre_playlists.get(reverse_mapping[genre])
                if genre_playlist_id:
                    try:
                        sp.playlist_add_items(genre_playlist_id, [track_ids[idx]])
                        sp.playlist_remove_all_occurrences_of_items(source_playlist_id, [track_ids[idx]])
                        print(f"Moved {track_info[idx][0]} by {track_info[idx][1]} to {reverse_mapping[genre]} playlist.")
                    except Exception as e:
                        print(f"Error moving {track_info[idx][0]}: {e}")
            
            # Clear batch lists
            track_ids = []
            track_info = []
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

move_songs_to_genre_playlists(source_playlist_id)
