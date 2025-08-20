import requests
import os
from dotenv import load_dotenv

def checkPlaying():
    load_dotenv()
    url = "https://api.spotify.com/v1/me/player"
    headers = {
        "Authorization": "Bearer " + os.getenv("SPOTIFY_ACCESS_TOKEN")
    }
    params = {
        "market": "GB"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return True
    elif response.status_code == 204:
        return False
    elif response.status_code == 401:
        print("Access token expired or invalid. Please refresh the token.")
        return None
    elif response.status_code == 403:
        print("Access forbidden. Check your permissions.")
        return None
    elif response.status_code == 429:
        print("Rate limit exceeded. Please try again later.")
        return None
    else:
        print(f"Unexpected error: {response.status_code} - {response.text}")
        return None

def getCurrentTrack():
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {
        "Authorization": "Bearer " + os.getenv("SPOTIFY_ACCESS_TOKEN")
    }
    params = {
        "market": "GB"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        track = data.get('item', {}).get('name', 'Unknown Track')
        artist = ', '.join([artist['name'] for artist in data.get('item', {}).get('artists', [])])
        album = data.get('item', {}).get('album', {}).get('name', 'Unknown Album')
        return track, artist, album
    else:
        print(f"Error fetching current track: {response.status_code} - {response.text}")
        return None, None, None