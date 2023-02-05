from marshmallow import Schema, fields
from schemas.SpotifyAccessInfoSchema import SpotifyAccessInfoSchema
from schemas.UserAttributesRequestSchema import UserAttributesRequestSchema


class GetUserRequestSchema(Schema):
    spotify_access_info = fields.Nested(SpotifyAccessInfoSchema, required=True)
