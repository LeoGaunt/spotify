from config import app
from flask import render_template, redirect
import requests
import os
from dotenv import load_dotenv
from utilities import checkPlaying, getCurrentTrack

@app.route('/')
def index():
    playing = checkPlaying()
    if playing is None:
        return redirect('/error')
    elif playing:
        return redirect('/playing')
    return redirect('/idle')

@app.route('/idle')
def idle():
    return render_template('idle.html')

@app.route('/playing')
def playing():
    playing = checkPlaying()
    if playing is None:
        return redirect('/error')
    elif not playing:
        return redirect('/idle')
    track, artist, album = getCurrentTrack()
    return render_template('playing.html', track=track, artist=artist, album=album)

@app.route('/error')
def error():
    return render_template('error.html')


if __name__ == '__main__':
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": "855f96d962fa471b916c7cd22d50ace9",
        "client_secret": "de860b487af94cd190c37cb3110e3c2a"
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