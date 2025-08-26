from config import app
from flask import render_template, redirect, request, session, send_file
import requests
from utilities import checkPlaying, getCurrentTrack, skipTrack, calculatePreviousListens, getAlbumCoverURL
from graphs import listens_by_week, plot_listens_image

# Spotify app credentials
CLIENT_ID = "855f96d962fa471b916c7cd22d50ace9"
CLIENT_SECRET = "de860b487af94cd190c37cb3110e3c2a"
REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Scopes required to read what I want to access
SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

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
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/login")
    playing = checkPlaying(session["access_token"])
    if playing is None:
        return redirect('/error')
    elif playing:
        return redirect('/playing')
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
    id, track, artist, album = getCurrentTrack(access_token)
    album_cover_url = getAlbumCoverURL(id, session["spotify_access_token"])
    previous_listens = calculatePreviousListens(id)
    return render_template('playing.html', track=track, artist=artist, album=album, previous_listens=previous_listens, album_cover_url=album_cover_url, id=id)

@app.route("/generate_graph/<track_id>")
def generate_graph(track_id):
    weeks, counts = listens_by_week(track_id)
    if weeks is None:
        return ""

    img = plot_listens_image(weeks, counts)
    return send_file(img, mimetype='image/png')

@app.route('/skip')
def skip():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/login")
    if skipTrack(access_token) == 0:
        return redirect('/playing')
    elif skipTrack(access_token) == 1:
        return redirect('/error')
    else:
        return redirect('/idle')

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run()