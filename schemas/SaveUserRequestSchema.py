from marshmallow import Schema, fields
from schemas.SpotifyAccessInfoSchema import SpotifyAccessInfoSchema
from schemas.UserAttributesRequestSchema import UserAttributesRequestSchema


class SaveUserRequestSchema(Schema):
    spotify_access_info = fields.Nested(SpotifyAccessInfoSchema, required=True)
    user_attributes = fields.Nested(UserAttributesRequestSchema)
