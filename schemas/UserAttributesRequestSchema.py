from marshmallow import Schema, fields


class UserAttributesRequestSchema(Schema):
    track_liked_tracks = fields.Boolean(required=True)
    track_shuffles = fields.Boolean(required=True)
