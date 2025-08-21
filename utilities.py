import requests

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
        track = data.get('item', {}).get('name', 'Unknown Track')
        artist = ', '.join([artist['name'] for artist in data.get('item', {}).get('artists', [])])
        album = data.get('item', {}).get('album', {}).get('name', 'Unknown Album')
        return track, artist, album
    else:
        print(f"Error fetching current track: {response.status_code} - {response.text}")
        return None, None, None