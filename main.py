from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

from controllers.spotify_auth_controller import *
from controllers.spotify_playlist_controller import *
from controllers.shuffle_controller import *

@app.route('/')
def status():
   return {"status": "healthy"}

if __name__ == '__main__':
   app.run()