import requests
import json
import os

def checkPlaying(user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = requests.get( "https://api.spotify.com/v1/me/player", headers=headers, params={"market": "GB"})
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

def getCurrentTrack(user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers, params={"market": "GB"})
    if response.status_code == 200:
        data = response.json()
        id = data.get('item', {}).get('id', 'Unknown ID')
        track = data.get('item', {}).get('name', 'Unknown Track')
        artist = ', '.join([artist['name'] for artist in data.get('item', {}).get('artists', [])])
        album = data.get('item', {}).get('album', {}).get('name', 'Unknown Album')
        return id, track, artist, album
    else:
        print(f"Error fetching current track: {response.status_code} - {response.text}")
        return None, None, None, None
    
def getDataFromID(track_id, spotify_access_token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {"Authorization": f"Bearer {spotify_access_token}"}
    response = requests.get(url, headers=headers, params={"market": "GB"})
    if response.status_code == 200:
        data = response.json()
        track = data.get('name', 'Unknown Track')
        artist = ', '.join([artist['name'] for artist in data.get('artists', [])])
        album = data.get('album', {}).get('name', 'Unknown Album')
        return track, artist, album
    else:
        print(f"Error fetching track data: {response.status_code} - {response.text}")
        return None, None, None
    
def skipTrack(user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
    if response.status_code == 204:
        return 0
    elif response.status_code == 401:
        print("Access token expired or invalid. Please refresh the token.")
        return 1
    elif response.status_code == 403:
        print("Access forbidden. Check your permissions.")
        return 1
    elif response.status_code == 404:
        print("No active device found. Please start playback on a device.")
        return 2
    elif response.status_code == 429:
        print("Rate limit exceeded. Please try again later.")
        return 1
    else:
        print(f"Unexpected error: {response.status_code} - {response.text}")
        return 1

def calculatePreviousListens(playing_track_id):
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "data")
    previous_listens = 0

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(".json"):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")
                    continue

                # Loop through each "play event" in the JSON
                for entry in data:
                    # Get track ID from URI
                    uri = entry.get("spotify_track_uri")
                    if uri:
                        track_id = uri.split(":")[-1]
                        if track_id == playing_track_id:
                            previous_listens += 1
    return previous_listens

def getAlbumCoverURL(playing_track_id, spotify_access_token):
    url = f"https://api.spotify.com/v1/tracks/{playing_track_id}"
    headers = {"Authorization": f"Bearer {spotify_access_token}"}
    response = requests.get(url, headers=headers, params={"market": "GB"})
    if response.status_code == 200:
        data = response.json()
        album_cover_url = data.get('album', {}).get('images', [{}])[0].get('url', '')
        return album_cover_url
    else:
        print(f"Error fetching album cover: {response.status_code} - {response.text}")
        return ''