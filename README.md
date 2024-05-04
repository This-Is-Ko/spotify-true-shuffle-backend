# Spotify True Shuffle - Backend

True Shuffle attempts to allow random shuffling by creating shuffled playlists with randomised order of tracks for a better shuffle experience.

Also has functionality to generate statistics and analysis from Spotify library, create playlists to share Liked Songs and delete all shuffled playlists.

Backend built on Flask in Python (Migrated from Spring Boot), deployed using Docker with containers for Flask (Gunicorn), Celery, Redis and Nginx.

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

Current set up to automatically deploy commits to the "main" branch using Railway

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

## Docker

Run 

    docker compose -f .\docker-compose-prod.yml build
    docker push [repository]:true_shuffle_flask_web
    docker push [repository]:true_shuffle_celery_worker

On machine running the server

    docker pull [repository]:true_shuffle_flask_web
    docker push [repository]:true_shuffle_celery_worker
    docker compose up -d

Docker reference

https://docs.docker.com/engine/install/ubuntu/

Generate SSL Cert (Ensure port 80 is free and instance firewall allows http and https)

    sudo certbot certonly --standalone -d api.trueshuffle.top
    
Mount the certificate directory in docker compose
    
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/nginx.conf
      - /etc/letsencrypt/live/api.trueshuffle.top:/etc/letsencrypt/live/api.trueshuffle.top
      - /etc/letsencrypt/archive/api.trueshuffle.top:/etc/letsencrypt/archive/api.trueshuffle.top

Update `./nginx/nginx.conf` to point to the certificate files

    ssl_certificate /etc/letsencrypt/live/api.trueshuffle.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.trueshuffle.top/privkey.pem;

## Troubleshooting

Potential cause of Gunicorn timeout due to Pymongo error. Add IP into DB network access "IP Access List"

https://stackoverflow.com/questions/41133455/docker-repository-does-not-have-a-release-file-on-running-apt-get-update-on-ubun