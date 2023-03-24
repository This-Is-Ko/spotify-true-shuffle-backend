from marshmallow import Schema, fields
from schemas.SpotifyAccessInfoSchema import SpotifyAccessInfoSchema


class ShufflePlaylistRequestSchema(Schema):
    playlist_id = fields.String(required=True)
    playlist_name = fields.String(required=True)
    is_use_liked_tracks = fields.Boolean()
    is_make_new_playlist = fields.Boolean()
