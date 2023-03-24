from marshmallow import Schema, fields
from schemas.SpotifyAccessInfoSchema import SpotifyAccessInfoSchema


class ShareLikedTracksRequestSchema(Schema):
    playlist_name = fields.String()
