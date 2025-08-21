from config import app
from flask import render_template, redirect, request, session, url_for
import requests
from utilities import checkPlaying, getCurrentTrack

# Spotify app credentials
CLIENT_ID = "855f96d962fa471b916c7cd22d50ace9"
CLIENT_SECRET = "de860b487af94cd190c37cb3110e3c2a"
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Scopes required to read what I want to access
SCOPE = "user-read-currently-playing user-read-playback-state"

# Authorization URL
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


@app.route('/')
def index():
    return redirect('/login')

@app.route("/login")
def login():
    auth_query = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID
    }
    return redirect(f"{AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in auth_query.items()])}")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=token_data)
    response_data = response.json()

    # Save tokens in session
    session["access_token"] = response_data.get("access_token")
    session["refresh_token"] = response_data.get("refresh_token")

    return redirect("/playing")


@app.route('/idle')
def idle():
    return render_template('idle.html')

@app.route('/playing')
def playing():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/login")
    playing = checkPlaying(session["access_token"])
    if playing is None:
        return redirect('/error')
    elif not playing:
        return redirect('/idle')
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    track, artist, album = getCurrentTrack(access_token)
    return render_template('playing.html', track=track, artist=artist, album=album)

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        # Update the .env file with the access token and overwite
        with open('.env', 'w') as f:
            f.write(f"SPOTIFY_ACCESS_TOKEN={access_token}\n")
        print("Access token saved to .env file.")
    else:
        print("Failed to get token:", response.status_code, response.text)
    app.run()