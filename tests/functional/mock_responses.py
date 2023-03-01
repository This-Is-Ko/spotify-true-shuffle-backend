
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


mock_no_liked_songs_tracks_response = {
    'href': 'https://api.spotify.com/v1/me/tracks?offset=0&limit=50',
    'limit': 50,
    'next': None,
    'offset': 0,
    'previous': None,
    'total': 0,
    "items": []
}
