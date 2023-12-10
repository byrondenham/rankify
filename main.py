import os
from os.path import join, dirname
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import itertools
import random

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Set up Spotify API credentials
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

# Authenticate with Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope='user-library-read'))

def get_user_playlist_id():
    playlist_id = input("Enter your Spotify playlist ID: ")
    return playlist_id

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return [track['track']['name'] for track in results['items']]

def get_user_preference(pair):
    # Simulate user preference (replace with actual user input)
    print(f"Which song do you prefer? {pair[0]} or {pair[1]}?")
    choice = input().strip().lower()
    return pair[0] if choice == pair[0].lower() else pair[1]

def pairwise_comparison(playlist_id):
    # Get playlist tracks
    playlist_tracks = get_playlist_tracks(playlist_id)

    # Generate all possible pairs of songs
    song_pairs = list(itertools.combinations(playlist_tracks, 2))

    # Initialise rankings
    rankings = {song: 0 for song in playlist_tracks}

    # Collect user preferences for each pair
    for pair in song_pairs:
        preference = get_user_preference(pair)

        # Update rankings based on user preference
        rankings[preference] += 1

    # Sort songs based on rankings
    sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return sorted_rankings

# Example usage
playlist_id = get_user_playlist_id()
final_ranking = pairwise_comparison(playlist_id)

print("Final Ranking:")
for song, score in final_ranking:
    print(f"{song}: {score} preferences")
