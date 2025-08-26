from flask import Flask, session
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CLIENT_ID = "855f96d962fa471b916c7cd22d50ace9"
CLIENT_SECRET = "de860b487af94cd190c37cb3110e3c2a"

@app.before_request
def check_valid_access_token():
    access_token = session.get("spotify_access_token")
    if not access_token:
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
            session["spotify_access_token"] = token_info['access_token']
        else:
            print("Failed to get token:", response.status_code, response.text)

# Import blueprints
from upload.views import upload_bp

app.register_blueprint(upload_bp)