from flask import Flask
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Import blueprints
from upload.views import upload_bp

app.register_blueprint(upload_bp)