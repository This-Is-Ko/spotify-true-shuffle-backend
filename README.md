# Spotify True Shuffle - Backend

Spotify's built-in shuffle pushes certain tracks rather than being randomly ordered.

True Shuffle creates custom playlists with randomised order of tracks for a better shuffle experience.

Also has functionality to generate statistics and analysis from Spotify library, create playlists to share Liked Songs and delete all shuffled playlists.

Backend built on Flask in Python (Migrated from Spring Boot)

Frontend can be found in [this](https://github.com/This-Is-Ko/spotify-true-shuffle-react) repository.

## Configure

The following env variables are required to run. Add them into a .env file

    SPOTIFY_CLIENT_ID # retrieve from Spotify Dev Console
    SPOTIFY_CLIENT_SECRET # retrieve from Spotify Dev Console
    SPOTIFY_REDIRECT_URI # frontend uri
    COOKIE_DOMAIN # cookie domain value (Leave empty for localhost)
    CORS_ORIGIN # cors origin value (http://localhost:3000)
    JWT_SECRET # secret to sign jwt
    JWT_ISSUER # issuer value for jwt
    MONGO_URI # database uri

To set the environment to the specific environment, set the following variable.

    # dev
    CONFIG_TYPE=config.DevelopmentConfig

    # test
    CONFIG_TYPE=config.TestingConfig

    # prod
    CONFIG_TYPE=config.ProductionConfig

## Run

Install dependancies:
    
    pip install -r requirements.txt

Run flask app:

    flask --app main.py run

## Deployment

Current set up to deploy onto Fly.io

    .venv\Scripts\activate 
    fly launch
    fly deploy

## Tests

Use pytest to run tests on the app:

    pytest

## Endpoints

`GET /api/spotify/auth/login`: Get Spotify login uri

`POST /api/spotify/auth/code`: Authenticate user with Spotify auth code

`POST /api/spotify/auth/logout`: Logout user and expire cookies

`GET /api/playlist/me`: Get playlists

`POST /api/playlist/shuffle`: Shuffle selected playlist

`DELETE /api/playlist/delete`: Delete all shuffled playlists

`POST /api/playlist/share/liked-tracks`: Create playlist from Liked Songs to share

`GET /api/user/`: Get user info

`GET /api/user/save`: Create/update user entry

`GET /api/user/tracker`: Get user tracker datapoints

`GET /api/user/analysis`: Get analysis of user's Liked Songs

`GET /api/user/aggregate`: Get analysis of user's Liked Songs and tracker datapoints in one call

`GET /api/statistics/overall`: Get shuffle statistics

`GET /api/trackers/update`: Update trackers for all enabled users

## Authentication

Authentication is handled by Spotify and the access-token/refresh-token are stored for each user. 

Sessions are created and send in cookies to the user which are revoked once logged out.
