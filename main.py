import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import itertools
import random
import json

app = Flask(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Set up Spotify API credentials
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")

# Authenticate with Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope='user-library-read'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/playlist', methods=['POST'])
def playlist():
    playlist_id = request.form.get('playlist_id')
    progress_file = 'progress.json'

    if playlist_id:
        final_ranking = pairwise_comparison(playlist_id, progress_file)
        return render_template('result.html', final_ranking=final_ranking)
    else:
        return redirect(url_for('index'))

def get_user_playlist_id():
    playlist_id = input("Enter your Spotify playlist ID: ")
    return playlist_id

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    return [track['track']['name'] for track in results['items']]

def get_user_preference(pair):
    print(f"Which song do you prefer? {pair[0]} or {pair[1]}?")
    partial_name = input().strip().lower()
    if partial_name in pair[0].lower():
        return pair[0]
    elif partial_name in pair[1].lower():
        return pair[1]
    else:
        print("Invalid input. Please enter a valid part of the song name.")
        return get_user_preference(pair)

def load_progress(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_progress(file_path, progress):
    with open(file_path, 'w') as file:
        json.dump(progress, file)

def pairwise_comparison(playlist_id, progress_file):
    # Get playlist tracks
    playlist_tracks = get_playlist_tracks(playlist_id)

    # Shuffle the list of songs
    random.shuffle(playlist_tracks)

    # Load progress from the file
    progress = load_progress(progress_file)

    # Initialise rankings
    rankings = progress.get('rankings', {song: 0 for song in playlist_tracks})

    # Get all possible pairs
    all_pairs = list(itertools.combinations(playlist_tracks, 2))

    # Continue presenting random pairs until all pairs are ranked
    while all_pairs:
        pair = random.choice(all_pairs)
        all_pairs.remove(pair)

        if pair not in progress.get('pairs_seen', []):
            preference = get_user_preference(pair)
            rankings[preference] += 1
            
            # Update the progress
            progress['pairs_seen'] = progress.get('pairs_seen', []) + [pair]
            progress['rankings'] = rankings
            save_progress(progress_file, progress)

    # Sort songs based on rankings
    sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return sorted_rankings

if __name__ == '__main__':
    app.run(debug=True)
