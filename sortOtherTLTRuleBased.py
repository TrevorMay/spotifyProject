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

genre_mapping['Rock'] = [
                        'Electronic rock', 
                        'Piano rock',
                        'French garage rock',
                        'Post-rock',
                        'English indie rock',
                        'South african rock',
                        'Irish rock',
                        'Soft rock',
                        'Hyper-rock',
                        'Canadian indie rock',
                        'Norwegian alternative rock',
                        'Pinoy rock',
                        'Korean indie rock',
                        'French stoner rock',
                        'J-rock',
                        'Norwegian rock',
                        'Australian indie rock',
                        'Yacht rock',
                        'Australian surf rock',
                        'Nyc indie rock',
                        'Modern alternative rock',
                        'Boston rock',
                        'Latin rock',
                        'Australian alternative rock',
                        'Geek rock', 
                        'Argentine alternative rock', 
                        'Alternative emo', 
                        'Alternative pop rock', 
                        'Acoustic rock', 
                        'Action rock', 
                        'Acoustic punk', 
                        '5th wave emo', 
                        'Rock', 
                        'Alternative rock', 
                        'Art rock', 
                        'Blues rock', 
                        'Instrumental rock', 
                        'Progressive rock', 
                        'Psychedelic rock', 
                        'Symphonic rock', 
                        'Slacker rock', 
                        'Roots rock', 
                        'Dance rock', 
                        'Modern rock', 
                        'Dance-punk', 
                        'Doo-wop', 
                        'Rock-and-roll', 
                        'Rockabilly', 
                        'Rock drums', 
                        'Album rock', 
                        'Classic rock', 
                        'Hard rock', 
                        'American post-punk', 
                        'Noise rock', 
                        'Funk rock', 
                        'Modern folk rock', 
                        'Austin rock', 
                        'Modern blues rock', 
                        'Glam rock', 
                        'Alternative metal', 
                        'Nu metal', 
                        'Rap metal',
                        'Oriental metal',
                        'Prog metal',
                        'Folk punk',
                        'Australian post-punk',
                        'Australian garage punk',
                        'Post-punk',
                        'Uk post-punk',
                        'Hardcore punk',
                        'Canadian post-punk',
                        'Uk post-punk revival',
                        'Melbourne punk',
                        'Vancouver punk',
                        'Riot grrrl',
                        'Rock alternatif francais',
                        'Rock en espanol']

# %%
genre_mapping['Indie'] = [
    'Auckland indie', 
    'Atlanta indie', 
    'Argentine indie', 
    'Albany ny indie', 
    'Sacramento indie', 
    'Indie rock', 
    'Chicago indie', 
    'La indie', 
    'Brooklyn indie', 
    'Indietronica', 
    'Indie soul', 
    'Indie', 
    'Kentucky indie', 
    'Kentucky roots', 
    'Bristol indie', 
    'Denton tx indie', 
    'Philly indie', 
    'Canadian indie', 
    'indie folk', 
    'Quebec indie', 
    'Austindie', 
    'Oxford indie', 
    'Bay area indie', 
    'Indie surf', 
    'Vancouver indie', 
    'Seattle indie', 
    'Indie punk', 
    'Indie pop', 
    'Lo-fi indie', 
    'Indie garage rock', 
    'Indie hip hop', 
    'Indie jazz', 
    'Indie psychedelic rock', 
    'Indie quebecois', 
    'Indie r&b', 
    'Indie singer-songwriter',
    'Portland indie',
    'Gainesville indie',
    'Louisville indie',
    'Victoria bc indie',
    'Nashville indie',
    'Tempe indie',
    'Canberra indie',
    'Polish indie',
    'Fort worth indie',
    'Taiwan indie',
    'French indietronica',
    'K-indie',
    'Minneapolis indie',
    'London indie',
    'Cardiff indie',
    'Perth indie',
    'Okc indie',
    'Experimental indie',
    'West yorkshire indie',
    'Socal indie',
    'Eugene indie',
    'Maine indie',
    'Australian indie',
    'Kansas indie',
    'Toronto indie',
    'Pov: indie',
    'Colombian indie',
    'Nz indie',
    'Pinoy indie',
    'Vienna indie',
    'Oakland indie',
    'Olympia wa indie',
    'Cape town indie',
    'Modern indie folk',
    'Columbus ohio indie',
    'Brighton indie',
    'Buffalo ny indie',
    'East anglia indie',
    'Boston indie',
    'Swiss indie',
    'Dutch indie',
    'Dublin indie',
    'Melbourne indie']

# %%
genre_mapping['Pop'] = [
    'Candy pop', 
    'Australian pop', 
    'Ambient pop', 
    '5th gen k-pop', 
    'Art pop', 
    'Dark pop', 
    'Chamber pop', 
    'Noise pop', 
    'Neo-synthpop', 
    'Vapor pop', 
    'Uk pop', 
    'Pop dance', 
    'german pop', 
    'New wav pop', 
    'Synthpop', 
    'Shimmer pop', 
    'Stomp pop', 
    'Modern jangle pop', 
    'Hyperpop', 
    'Proto-hyperpop', 
    'Transpop', 
    'Power pop', 
    'Baroque pop', 
    'Hypnagogic pop', 
    'Pop', 
    'Pop electronico', 
    'Pop nacional', 
    'Pop punk', 
    'Pop rap', 
    'Pop soul',
    'French indie pop',
    'J-pop',
    'Canadian pop',
    'Chill pop',
    'K-pop girl group',
    'Singer-songwriter pop',
    'Danish indie pop',
    'Polish pop',
    'Psychedelic pop',
    'Space age pop',
    'Italian adult pop',
    'Japanese alternative pop',
    'Japanese indie pop',
    'Taiwan pop',
    'New wave pop',
    'Korean electropop',
    'French synthpop',
    'Japanese teen pop',
    'Classic city pop',
    'Nyc pop',
    'Experimental pop',
    'Mandopop',
    'Metropopolis',
    'Uk alternative pop',
    'K-pop',
    'Sophisti-pop',
    'Bedroom pop',
    'Indie electropop',
    'Colombian pop',
    'Glitch pop',
    'Japanese bedroom pop',
    'Italian pop',
    'K-pop boy group',
    'Classic italian pop',
    'La pop',
    'Chill dream pop',
    'Modern dream pop',
    'German pop',
    'Hip pop',
    'Twee pop',
    'City pop',
    'Dance pop',
    'Gauze pop',
    'Swedish synthpop',
    'Korean city pop',
    'Collage pop',
    'Modern indie pop',
    'Puerto rican pop',
    'Swedish pop',
    'Australian alternative pop']

# %%
genre_mapping['EDM'] = [
    'Aussietronica', 
    'Ambient', 
    'Alternative dance', 
    'Electronica', 
    'Laboratorio', 
    'Lo-fi', 
    'Rave', 
    'Hardcore techno', 
    'New rave', 
    'Chillwave', 
    'Edm', 
    'Electro house', 
    'Deep tropical house', 
    'Pop edm', 
    'Progressive electro house', 
    'Tropical house', 
    'Ambient psychill', 
    'Psychill', 
    'Vaporwave',
    'Experimental house',
    'Stutter house',
    'Filter house',
    'Witch house',
    'Vocal house',
    'Disco house',
    'German house',
    'Jazz house',
    'Float house',
    'Outsider house',
    'Swedish house',
    'Intelligent dance music',
    'Uk dance',
    'Alternative dance',
    'Norwegian techno',
    'German techno',
    'Hard techno',
    'Dub techno',
    'Minimal techno',
    'Polish electronica',
    'Russian electronic',
    'South african electronic',
    'Colombian electronic',
    'Portuguese electronic',
    'Uk experimental electronic',
    'Leipzig electronic',
    'Nz electronic',
    'Boston electronic',
    'Glitchbreak',
    'Glitchcore']

# %%
genre_mapping['Rap'] = [
    'Atl hip hop', 
    'Afrobeat', 
    'Afrofuturism', 
    'Abstract hip hop', 
    'Trip hop', 
    'Big beat', 
    'Breakbeat', 
    'Funky breaks', 
    'Bboy', 
    'Nz hip hop', 
    'Nz jazz', 
    'Instrumental hip hop', 
    'Japanese chillhop', 
    'Japanese old school hip hop', 
    'Jazz rap', 
    'Alternative hip hop', 
    'Hip hop',
    'Melodic rap',
    'Trap soul',
    'Dark trap',
    'Cincinnati rap',
    'K-rap',
    'Cloud rap',
    'Cali rap',
    'Trap latino',
    'Pittsburgh rap',
    'Trap queen',
    'German alternative rap',
    'Dfw rap',
    'Sad rap',
    'Meme rap',
    'German hip hop',
    'Chill abstract hip hop',
    'Canadian hip hop',
    'Greek hip hop',
    'Czsk hip hop',
    'Uk alternative hip hop',
    'Czech hip hop',
    'Experimental hip hop',
    'Portland hip hop',
    'Birmingham hip hop',
    'Minnesota hip hop']

# %%
genre_mapping['Other'] = [
    'Anti-folk', 
    'Alt z', 
    'Alternative americana', 
    'Adult standards', 
    'Experimental Songs', 
    'Zolo', 
    'Folk', 
    'Singer-songwriter', 
    'Elephant 6', 
    'Stomp and holler', 
    'Metropolis', 
    'Alternative dance', 
    'Instrumental funk', 
    'Rare groove', 
    'Stutter house', 
    'Talentschau', 
    'Disco', 
    'Freestyle', 
    'Funk', 
    'Minneapolis sound', 
    'New jack swing', 
    'Quiet storm', 
    'Urban contemporary', 
    'Mellow gold', 
    'Uk americana', 
    'New romantic', 
    'Neo-psychedelic', 
    'Downtempo', 
    'New wave', 
    'Permanent wave', 
    'Uk post-punk', 
    'Shoegaze', 
    'Filter house', 
    'Nu disco', 
    'Melancholia', 
    'Slowcore', 
    'Progressive post-hardcore', 
    'Intelligent dance music', 
    'Bubblegum bass', 
    'Deconstructed club', 
    'Escape room',
    '21st century classical',
    'Adult standards',
    'Alt z',
    'Alternative americana',
    'American contemporary classical',
    'Anthem worship',
    'Anti-folk',
    'Australian psych',
    'Australian singer-songwriter',
    'Banjo',
    'Baroque',
    'Beatlesque',
    'Bebop',
    'Bluegrass',
    'Brazilian experimental',
    'Breakcore',
    'British contemporary classical',
    'British singer-songwriter',
    'Bubblegrunge',
    'Bubblegum bass',
    'Canadian psychedelic',
    'Cantautora argentina',
    'Cascadia shoegaze',
    'Chamber psych',
    'Chill lounge',
    'Classic soundtrack',
    'Classical',
    'Comfy synth',
    'Comic',
    'Compositional ambient',
    'Contemporary classical',
    'Crank wave',
    'Dancefloor dnb',
    'Dariacore',
    'Deconstructed club',
    'Disco',
    'Diy emo',
    'Double drumming',
    'Downtempo',
    'Drain',
    'Dreamgaze',
    'Dreamo',
    'Drum and bass',
    'Early avant garde',
    'Early modern classical',
    'Early music',
    'Easy listening',
    'Electrofox',
    'Elephant 6',
    'Emo',
    'Escape room',
    'Experimental ambient',
    'Experimental vocal',
    'Fluxwork',
    'Folk',
    'Folklore boliviano',
    'Fourth world',
    'Freestyle',
    'French psychedelic',
    'Funk',
    'Funk carioca',
    'Funk mandelao',
    'Funk mtg',
    'Funktronica',
    'Future funk',
    'Future garage',
    'Gen z singer-songwriter',
    'German baroque',
    'Glitchbreak',
    'Glitchcore',
    'Grungegaze',
    'Hard bop',
    'Hexd',
    'High-tech minimal',
    'Hip-hop experimental',
    'Icelandic classical',
    'Impressionism',
    'Indie anthem-folk',
    'Indie folk',
    'Instrumental funk',
    'Irish neo-traditional',
    'J-division',
    'J-reggae',
    'Jam band',
    'Jamtronica',
    'Japanese classical',
    'Japanese contemporary classical',
    'Japanese experimental',
    'Japanese idm',
    'Japanese juke',
    'Japanese piano',
    'Japanese shoegaze',
    'Japanese soundtrack',
    'Japanese vtuber',
    'Jazz piano',
    'Jazz saxophone',
    'Jump blues',
    'Korean ost',
    'Korean shoegaze',
    'Latin alternative',
    'Latin talent show',
    'Latintronica',
    'Livetronica',
    'Mandolin',
    'Melancholia',
    'Mellow gold',
    'Microtonal',
    'Minimalism',
    'Minneapolis sound',
    'Modern melodic hardcore',
    'Mongolian alternative',
    'Multidisciplinary',
    'Musica andina',
    'Musica indigena latinoamericana',
    'Neo-classical',
    'Neo-psychedelic',
    'Neoclassical darkwave',
    'Neoclassicism',
    'Neue neue deutsche welle',
    'New isolationism',
    'New jack swing',
    'New romantic',
    'New wave',
    'Nova musica carioca',
    'Nu disco',
    'Nu gaze',
    'Opm',
    'Pastoral',
    'Permanent wave',
    'Phonk brasileiro',
    'Plugg',
    'Post-minimalism',
    'Post-romantic era',
    'Progressive post-hardcore',
    'Punk',
    'Queercore',
    'Quiet storm',
    'Rap',
    'Rap italiano old school',
    'Rare groove',
    'Reggaeton',
    'Rif',
    'Riot grrrl',
    'Rock alternatif francais',
    'Rock en espanol',
    'Russian emo',
    'Shoegaze',
    'Singer-songwriter',
    'Slowcore',
    'Small room',
    'Solo wave',
    'South african alternative',
    'Spacegrunge',
    'Spectra',
    'Stomp and holler',
    'Swedish experimental',
    'Talentschau',
    'Tape club',
    'Texasgaze',
    'Trance',
    'Turkish psych',
    'Uilleann pipes',
    'Uk americana',
    'Uk bass',
    'Uk garage',
    'Urban contemporary',
    'Urbano espanol',
    'Urbano latino',
    'Violao',
    'Wave',
    'Wonky',
    'World',
    'World fusion',
    'Ye ye',
    'Zolo',
    'Zoomergaze']

# %%
genre_mapping['Jazz'] = [
    'Jazz fusion', 
    'Jazz rock', 
    'Unknown', 
    'New americana', 
    'Roots americana', 
    'Southern americana', 
    'Progressive jazz fusion', 
    'Contemporary jazz', 
    'Jazz',
    'Canadian modern jazz',
    'Danish modern jazz',
    'Uk contemporary jazz',
    'Experimental jazz',
    'Classic japanese jazz',
    'Free jazz',
    'Modern jazz piano',
    'Swedish jazz',
    'Cool jazz',
    'Swiss jazz',
    'Norwegian jazz',
    'Ecm-style jazz',
    'Psychedelic jazz fusion',
    'Smooth jazz']

# %%
genre_mapping['Country'] = [
    'Alternative country', 
    'Countrygaze']

# %%
genre_mapping['Soul_RB'] = [
    'Uk contemporary r&b', 
    'Alternative r&b', 
    'Motown', 
    'Soul',
    'Experimental r&b',
    'Japanese r&b',
    'Canadian contemporary r&b',
    'Bedroom r&b',
    'Korean r&b',
    'Instrumental soul',
    'Retro soul',
    'Bedroom soul',
    'Neo soul',
    'British soul']

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
print(f'length of tracks: {len(tracks)}')
print('made it past tracks request')

while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

print('made it past results')
print(f'length of results: {len(results)}')

print(f'length of tracks after results {len(tracks)}')

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
        print('EXCEPTION RAISED 1')
        print(f"track id: {track_id}")
        print(f"artist id: {artist_id}")
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
    print(f'genre: {genre}')
    if genre != 'Other':
        genre_playlist_id = playlist_genre_mapping[genre]
        if genre_playlist_id ==  "P36gcPJgStoWudUwX0ZCC":
            track_uris = [item.split(':')[-1] for item in track_uris]
            print("pop track uris")
        try:
            sp.user_playlist_add_tracks(user_id, genre_playlist_id, track_uris) # add tracks to genre specific playlist
            sp.playlist_remove_all_occurrences_of_items(playlist_genre_mapping['Other'], track_uris) # remove tracks from 'Other TLT'
            print(f"Added {len(track_uris)} songs to '{genre}'")
        except Exception as e:
            print('EXCEPTION RAISED 2')
            print(Exception)
            print(f"genre playlist id: {genre_playlist_id}")
            
print("Done!")

# %%
unmapped_genres

# %%
items_to_remove = []

for item in unmapped_genres:
    if 'soul' in item:
        print(f"'{item}',")
        items_to_remove.append(item)

for item in items_to_remove:
    unmapped_genres.remove(item)

# %%
for genre, track_uris in genre_tracks.items():
    print(genre)
    print(len(track_uris))

# %%
playlist_genre_mapping

# %%
genre_tracks
