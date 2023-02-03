from marshmallow import Schema, fields
from schemas.SpotifyAccessInfoSchema import SpotifyAccessInfoSchema


class SpotifyAccessInfoRequestSchema(Schema):
    spotify_access_info = fields.Nested(SpotifyAccessInfoSchema, required=True)
