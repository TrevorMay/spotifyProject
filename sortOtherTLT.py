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
                                               scope='playlist-read-private playlist-modify-private playlist-modify-public'))

# %%
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
genre_mapping = dict()

genre_mapping['Rock'] = ['Argentine alternative rock', 'Alternative emo', 'Alternative pop rock', 'Acoustic rock', 'Action rock', 'Acoustic punk', '5th wave emo', 'Rock', 'Alternative rock', 'Art rock', 'Blues rock', 'Instrumental rock', 'Progressive rock', 'Psychedelic rock', 'Symphonic rock', 'Slacker rock', 'Roots rock', 'Dance rock', 'Modern rock', 'Dance-punk', 'Doo-wop', 'Rock-and-roll', 'Rockabilly', 'Rock drums', 'Album rock', 'Classic rock', 'Hard rock', 'American post-punk', 'Noise rock', 'Funk rock', 'Modern folk rock', 'Austin rock', 'Modern blues rock', 'Glam rock', 'Alternative metal', 'Nu metal', 'Rap metal']

genre_mapping['Indie'] = ['Auckland indie', 'Atlanta indie', 'Argentine indie', 'Albany ny indie', 'Sacramento indie', 'Indie rock', 'Chicago indie', 'La indie', 'Brooklyn indie', 'Indietronica', 'Indie soul', 'Indie', 'Kentucky indie', 'Kentucky roots', 'Bristol indie', 'Denton tx indie', 'Philly indie', 'Canadian indie', 'indie folk', 'Quebec indie', 'Austindie', 'Oxford indie', 'Bay area indie', 'Indie surf', 'Vancouver indie', 'Seattle indie', 'Indie punk', 'Indie pop', 'Lo-fi indie', 'Indie garage rock', 'Indie hip hop', 'Indie jazz', 'Indie psychedelic rock', 'Indie quebecois', 'Indie r&b', 'Indie singer-songwriter']

genre_mapping['Pop'] = ['Candy pop', 'Australian pop', 'Ambient pop', '5th gen k-pop', 'Art pop', 'Dark pop', 'Chamber pop', 'Noise pop', 'Neo-synthpop', 'Vapor pop', 'Uk pop', 'Pop dance', 'german pop', 'New wav pop', 'Synthpop', 'Shimmer pop', 'Stomp pop', 'Modern jangle pop', 'Hyperpop', 'Proto-hyperpop', 'Transpop', 'Power pop', 'Baroque pop', 'Hypnagogic pop', 'Pop', 'Pop electronico', 'Pop nacional', 'Pop punk', 'Pop rap', 'Pop soul',]

genre_mapping['EDM'] = ['Aussietronica', 'Ambient', 'Alternative dance', 'Electronica', 'Laboratorio', 'Lo-fi', 'Rave', 'Hardcore techno', 'New rave', 'Chillwave', 'Edm', 'Electro house', 'Deep tropical house', 'Pop edm', 'Progressive electro house', 'Tropical house', 'Ambient psychill', 'Psychill', 'Vaporwave']

genre_mapping['Rap'] = ['Atl hip hop', 'Afrobeat', 'Afrofuturism', 'Abstract hip hop', 'Trip hop', 'Big beat', 'Breakbeat', 'Funky breaks', 'Bboy', 'Nz hip hop', 'Nz jazz', 'Instrumental hip hop', 'Japanese chillhop', 'Japanese old school hip hop', 'Jazz rap', 'Alternative hip hop', 'Hip hop']

genre_mapping['Other'] = ['Anti-folk', 'Alt z', 'Alternative americana', 'Adult standards', 'Experimental Songs', 'Zolo', 'Folk', 'Singer-songwriter', 'Elephant 6', 'Stomp and holler', 'Metropolis', 'Alternative dance', 'Instrumental funk', 'Rare groove', 'Stutter house', 'Talentschau', 'Disco', 'Freestyle', 'Funk', 'Minneapolis sound', 'New jack swing', 'Quiet storm', 'Urban contemporary', 'Mellow gold', 'Uk americana', 'New romantic', 'Neo-psychedelic', 'Downtempo', 'New wave', 'Permanent wave', 'Uk post-punk', 'Shoegaze', 'Filter house', 'Nu disco', 'Melancholia', 'Slowcore', 'Progressive post-hardcore', 'Intelligent dance music', 'Bubblegum bass', 'Deconstructed club', 'Escape room']

genre_mapping['Jazz'] = ['Jazz fusion', 'Jazz rock', 'Unknown', 'New americana', 'Roots americana', 'Southern americana', 'Progressive jazz fusion', 'Contemporary jazz', 'Jazz']

genre_mapping['Country'] = ['Alternative country', 'Countrygaze']

genre_mapping['Soul_RB'] = ['Uk contemporary r&b', 'Alternative r&b', 'Motown', 'Soul']

# %%
# Fetch the current user's playlists
playlists = sp.current_user_playlists()

# Display the playlists and their IDs
for playlist in playlists['items']:
    if 'TLT' in playlist['name']:
        print(f"Name: {playlist['name']}, ID: {playlist['id']}")

print("All playlists fetched successfully!")

# %%
playlist_genre_mapping = {'Pop': 'P36gcPJgStoWudUwX0ZCC',
                          'Country': '6s7uiLkGuV19avNRwdWIIj',
                          'Soul_RB': '6hEJKk2mF1uBG50G6bsmbF',
                          'EDM': '1d6b5iJk8QjWEs6FrR1JPI',
                          'Rap': '6jRyO0OAe3JUYv92YrNLFq',
                          'Rock': '6OsJ4cmdvodbqHKHO4fUNg',
                          'Indie': '2pKInR4KBvpIbp28FWm3tE',
                          'Jazz': '4Om6SVyGS7C7M4i0gyds0E',
                          'Other': '6fbYFsJU3Fz6uIkooJvIbq'} 

# %%
# Remove the cached token file
if os.path.exists('.cache'):
    os.remove('.cache')

# %%
# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-read-private playlist-modify-private playlist-modify-public'))

# %%
access_token = get_access_token(client_id, client_secret)
if access_token:
    print(f"Access token: {access_token}")
else:
    print("Failed to obtain access token.")

# %%
import random

unmapped_genres = set()

# Headers for the GET request, including the access token
headers = {
    'Authorization': f'Bearer {access_token}'
}

# Get user ID
user_id = sp.current_user()['id']

# Replace with your playlist name
playlist_name = "Other TLT"

# Find the playlist ID
playlists = sp.user_playlists(user_id)
print('made it past playlists request')
playlist_id = None

for playlist in playlists['items']:
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

artists_seen = set()

# Analyze each track and sort by genre
for item in tracks:
    track = item['track']
    track_id = track['id']

    # Get genre information from artist
    artist_id = track['artists'][0]['id']
    endpoint = f'https://api.spotify.com/v1/artists?ids={artist_id}' 
    if artist_id not in artists_seen:
        artists_seen.add(artist_id)
        try:
            response = requests.get(endpoint, headers=headers)
            while response.status_code == 429:
                retry_after = int(response.headers['retry-after'])
                retry_after = retry_after + random.randint(1, 10)
                print('sleeping ' + str(retry_after) + ' seconds')
                time.sleep(retry_after)
                response = requests.get(endpoint, headers=headers)
            response = response.json()
        except Exception as e:
            print('EXCEPTION RAISED')
            print(response.status_code)
            print(response)
            print(e)
            raise
        genre = 'Other' # set to Other as a default
        matching_key = 'Other' # set to Other as a default
        if 'artists' in response.keys(): 
            for artist in response['artists']: # for each artist
                if artist is not None:
                    if len(artist['genres']) > 0: # if there are genres associated with the artist
                        for genre in artist['genres']: # for each genre see if it's in our mapping
                            genre = genre.capitalize()
                            for key, genre_list in genre_mapping.items(): # go through each genre mapping list to try and find artist genre
                                for value in genre_list:
                                    if value == genre:
                                        matching_key = key # We found the larger genre of the artist's microgenre!
                            if matching_key == 'Other': # if matching_key still equals other that means we haven't mapped this micro_genre
                                unmapped_genres.add(genre)

        if matching_key not in genre_tracks:
            genre_tracks[matching_key] = []

        genre_tracks[matching_key].append(track['uri'])

# add tracks by genre
for genre, track_uris in genre_tracks.items():
    if genre != 'Other':
        genre_playlist_id = playlist_genre_mapping[genre]
        try:
            sp.user_playlist_add_tracks(user_id, genre_playlist_id, track_uris) # add tracks to genre specific playlist
            sp.playlist_remove_all_occurrences_of_items(playlist_genre_mapping['Other'], track_uris) # remove tracks from 'Other TLT'
            print(f"Added {len(track_uris)} songs to '{genre}'")
        except Exception as e:
            print('EXCEPTION RAISED')
            print(Exception)
            
print("Done!")

# %%
for item in tracks:
    track = item['track']
    track_id = track['id']
    print(track_id)

# %%
unmapped_genres
