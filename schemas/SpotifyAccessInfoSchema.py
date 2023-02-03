from marshmallow import Schema, fields


class SpotifyAccessInfoSchema(Schema):
    token_type = fields.String(required=True)
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    expires_at = fields.Integer(required=True)
    scope = fields.String(required=True)
