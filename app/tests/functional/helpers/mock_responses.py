
mock_user_response = {
    "country": "country_sample",
    "display_name": "display_name_sample",
    "email": "email_sample",
    "external_urls": {
        "spotify": "spotify_sample"
    },
    "followers": {
        "href": "href_sample",
        "total": 1
    },
    "href": "href_sample",
    "id": "id_sample",
    "uri": "uri_sample"
}

mock_user_details_response = {
    "id": "user_id"
}

mock_user_playlists_sample = {
    "items": [
        {
            "collaborative": True,
            "description": "string",
            "external_urls": {
                "spotify": "string"
            },
            "href": "string",
            "id": "string",
            "images": [
                {
                  "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                  "height": 300,
                  "width": 300
                }
            ],
            "name": "string",
            "owner": {
                "external_urls": {
                    "spotify": "string"
                },
                "followers": {
                    "href": "string",
                    "total": 0
                },
                "href": "string",
                "id": "string",
                "type": "user",
                "uri": "string",
                "display_name": "string"
            },
            "public": True,
            "snapshot_id": "string",
            "tracks": {
                "href": "string",
                "total": 0
            },
            "type": "string",
            "uri": "string"
        },
        {
            "collaborative": True,
            "description": "images is None",
            "external_urls": {
                "spotify": "string"
            },
            "href": "string",
            "id": "string",
            "images": None,
            "name": "string",
            "owner": {
                "external_urls": {
                    "spotify": "string"
                },
                "followers": {
                    "href": "string",
                    "total": 0
                },
                "href": "string",
                "id": "string",
                "type": "user",
                "uri": "string",
                "display_name": "string"
            },
            "public": True,
            "snapshot_id": "string",
            "tracks": {
                "href": "string",
                "total": 0
            },
            "type": "string",
            "uri": "string"
        },
        {
            "collaborative": True,
            "description": "images is misspelt - real api response edge case",
            "external_urls": {
                "spotify": "string"
            },
            "href": "string",
            "id": "string",
            "imag@es": [
                {
                  "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                  "height": 300,
                  "width": 300
                }
            ],
            "name": "string",
            "owner": {
                "external_urls": {
                    "spotify": "string"
                },
                "followers": {
                    "href": "string",
                    "total": 0
                },
                "href": "string",
                "id": "string",
                "type": "user",
                "uri": "string",
                "display_name": "string"
            },
            "public": True,
            "snapshot_id": "string",
            "tracks": {
                "href": "string",
                "total": 0
            },
            "type": "string",
            "uri": "string"
        }
    ],
    "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20\n",
    "limit": 20,
    "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "offset": 0,
    "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "total": 3
}

mock_tracks_response = {
    'href': 'https://api.spotify.com/v1/me/tracks?offset=0&limit=50',
    'limit': 50,
    'next': 'https://api.spotify.com/v1/me/tracks?offset=50&limit=50',
    'offset': 0,
    'previous': None,
    'total': 2,
    "items": [
        {
            'added_at': '2023-02-28T08:48:22Z',
            'track': {
                'album': {
                    'album_type': 'album',
                    'artists': [
                        {
                            'external_urls': {
                                'spotify': 'https://open.spotify.com/artist/4xRYI6VqpkE3UwrDrAZL8L'
                            },
                            'href': 'https://api.spotify.com/v1/artists/4xRYI6VqpkE3UwrDrAZL8L',
                            'id': '4xRYI6VqpkE3UwrDrAZL8L0',
                            'name': 'Logic0',
                            'type': 'artist',
                            'uri': 'spotify:artist:4xRYI6VqpkE3UwrDrAZL8L'
                        }
                    ],
                    'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU'],
                    'external_urls': {
                        'spotify': 'https://open.spotify.com/album/7C5J8fG34IbOKe2pQPq9SU'
                    },
                    'href': 'https://api.spotify.com/v1/albums/7C5J8fG34IbOKe2pQPq9SU',
                    'id': '7C5J8fG34IbOKe2pQPq9SU0',
                    'images': [
                        {
                            'height': 640,
                            'url': 'https://i.scdn.co/image/ab67616d0000b273ba518c4c580b3652111c7c84',
                            'width': 640
                        }
                    ],
                    'name': 'Supermarket (Soundtrack)0',
                    'release_date': '2019-03-26',
                    'release_date_precision': 'day',
                    'total_tracks': 13,
                    'type': 'album',
                    'uri': 'spotify:album:7C5J8fG34IbOKe2pQPq9SU'},
                'artists': [
                    {
                        'external_urls': {
                            'spotify': 'https://open.spotify.com/artist/4xRYI6VqpkE3UwrDrAZL8L'
                        },
                        'href': 'https://api.spotify.com/v1/artists/4xRYI6VqpkE3UwrDrAZL8L',
                        'id': '4xRYI6VqpkE3UwrDrAZL8L0',
                        'name': 'Logic0',
                        'type': 'artist',
                        'uri': 'spotify:artist:4xRYI6VqpkE3UwrDrAZL8L'
                    }
                ],
                'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU'],
                'disc_number': 1,
                'duration_ms': 183000,
                'explicit': True,
                'external_ids': {
                    'isrc': 'USUM71904188'
                },
                'external_urls': {
                    'spotify': 'https://open.spotify.com/track/5cJBMRBaLTxrT02SSaoPJO'
                },
                'href': 'https://api.spotify.com/v1/tracks/5cJBMRBaLTxrT02SSaoPJO',
                'id': '5cJBMRBaLTxrT02SSaoPJO',
                'is_local': False,
                'name': 'Supermarket0',
                'popularity': 39,
                'preview_url': 'https://p.scdn.co/mp3-preview/9edf9d251d05ddfac3708582925905c31274668a?cid=6e3003b1e8c348a3bf2e438957bb095e',
                'track_number': 9,
                'type': 'track',
                'uri': 'spotify:track:5cJBMRBaLTxrT02SSaoPJO'
            }
        },
        {
            'added_at': '2023-02-27T08:48:22Z',
            'track': {
                'album': {
                    'album_type': 'album',
                    'artists': [
                        {
                            'external_urls': {
                                'spotify': 'https://open.spotify.com/artist/4xRYI6VqpkE3UwrDrAZL8L'
                            },
                            'href': 'https://api.spotify.com/v1/artists/4xRYI6VqpkE3UwrDrAZL8L',
                            'id': '4xRYI6VqpkE3UwrDrAZL8L1',
                            'name': 'Logic1',
                            'type': 'artist',
                            'uri': 'spotify:artist:4xRYI6VqpkE3UwrDrAZL8L'
                        }
                    ],
                    'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU'],
                    'external_urls': {
                        'spotify': 'https://open.spotify.com/album/7C5J8fG34IbOKe2pQPq9SU'
                    },
                    'href': 'https://api.spotify.com/v1/albums/7C5J8fG34IbOKe2pQPq9SU',
                    'id': '7C5J8fG34IbOKe2pQPq9SU1',
                    'images': [
                        {
                            'height': 640,
                            'url': 'https://i.scdn.co/image/ab67616d0000b273ba518c4c580b3652111c7c84',
                            'width': 640
                        }
                    ],
                    'name': 'Supermarket (Soundtrack)1',
                    'release_date': '2019-03-26',
                    'release_date_precision': 'day',
                    'total_tracks': 13,
                    'type': 'album',
                    'uri': 'spotify:album:7C5J8fG34IbOKe2pQPq9SU'},
                'artists': [
                    {
                        'external_urls': {
                            'spotify': 'https://open.spotify.com/artist/4xRYI6VqpkE3UwrDrAZL8L'
                        },
                        'href': 'https://api.spotify.com/v1/artists/4xRYI6VqpkE3UwrDrAZL8L',
                        'id': '4xRYI6VqpkE3UwrDrAZL8L1',
                        'name': 'Logic1',
                        'type': 'artist',
                        'uri': 'spotify:artist:4xRYI6VqpkE3UwrDrAZL8L'
                    }
                ],
                'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU'],
                'disc_number': 1,
                'duration_ms': 183000,
                'explicit': True,
                'external_ids': {
                    'isrc': 'USUM71904188'
                },
                'external_urls': {
                    'spotify': 'https://open.spotify.com/track/5cJBMRBaLTxrT02SSaoPJO'
                },
                'href': 'https://api.spotify.com/v1/tracks/5cJBMRBaLTxrT02SSaoPJO',
                'id': '5cJBMRBaLTxrT02SSaoPJO1',
                'is_local': False,
                'name': 'Supermarket1',
                'popularity': 39,
                'preview_url': 'https://p.scdn.co/mp3-preview/9edf9d251d05ddfac3708582925905c31274668a?cid=6e3003b1e8c348a3bf2e438957bb095e',
                'track_number': 9,
                'type': 'track',
                'uri': 'spotify:track:5cJBMRBaLTxrT02SSaoPJO'
            }
        }
    ]
}

empty_all_user_playlists_response_sample = {
    "items": [
    ]
}

mock_no_liked_songs_tracks_response = {
    'href': 'https://api.spotify.com/v1/me/tracks?offset=0&limit=50',
    'limit': 50,
    'next': None,
    'offset': 0,
    'previous': None,
    'total': 0,
    "items": []
}

mock_audio_features_response = {
    "audio_features": [
        {
            "acousticness": 0.00242,
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B\n",
            "danceability": 0.585,
            "duration_ms": 237040,
            "energy": 0.842,
            "id": "2takcwOaAZWiXQijPHIx7B",
            "instrumentalness": 0.00686,
            "key": 9,
            "liveness": 0.0866,
            "loudness": -5.883,
            "mode": 0,
            "speechiness": 0.0556,
            "tempo": 118.211,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B\n",
            "type": "audio_features",
            "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
            "valence": 0.428
        },
        {
            "acousticness": 0.00242,
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B\n",
            "danceability": 0.585,
            "duration_ms": 237040,
            "energy": 0.842,
            "id": "2takcwOaAZWiXQijPHIx7B",
            "instrumentalness": 0.00686,
            "key": 9,
            "liveness": 0.0866,
            "loudness": -5.883,
            "mode": 0,
            "speechiness": 0.0556,
            "tempo": 118.211,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B\n",
            "type": "audio_features",
            "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
            "valence": 0.428
        }
    ]
}
