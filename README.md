# Spotify True Shuffle - Backend

Spotify's built-in shuffle pushes certain tracks rather than being randomly ordered.

True Shuffle creates custom playlists with randomised order of tracks for a better shuffle experience.

Backend built on Flask in Python (Migrated from Spring Boot)

Frontend can be found in [this](https://github.com/This-Is-Ko/spotify-true-shuffle-react) repository.

## Configure

The following env variables are required to run. Add them into a .env file

    SPOTIPY_CLIENT_ID # retrieve from Spotify Dev Console
    SPOTIPY_CLIENT_SECRET # retrieve from Spotify Dev Console
    SPOTIPY_REDIRECT_URI # frontend uri
    COUNTER_DIRECTORY # point to directory where counters are stored

To set the environment to the specific environment, set the following variable.

    # dev
    CONFIG_TYPE=config.DevelopmentConfig

    # test
    CONFIG_TYPE=config.TestingConfig

    # prod
    CONFIG_TYPE=config.ProductionConfig

## Run

Run flask app:

    flask --app main.py run

## Deployment

Current set up to automatically deploy commits to the "main" branch using PythonAnywhere

## Tests

Use pytest to run tests on the app:

    pytest

## Endpoints

`GET /api/spotify/auth/login`: Get Spotify login uri

`POST /api/spotify/auth/code`: Authenticate user with Spotify auth code

`POST /api/spotify/me/playlists`: Retrieve Playlists

`POST /api/playist/shuffle`: Shuffle Playlist

`POST /api/playist/delete`: Shuffle Playlist

`GET /api/statistics/overall`: Get usage statistics
