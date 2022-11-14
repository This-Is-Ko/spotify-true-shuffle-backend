from main import app
from flask import request

from services import spotify_auth_service

@app.route('/api/spotify/auth/login', methods=['GET'])
def get_spotify_uri():
    auth_uri = spotify_auth_service.generate_spotify_auth_uri()
    return {"loginUri": auth_uri}

@app.route('/api/spotify/auth/code', methods=['POST'])
def handle_auth_code():
    data = request.get_json()
    code = str (data["code"])
    return spotify_auth_service.get_spotify_tokens(code)