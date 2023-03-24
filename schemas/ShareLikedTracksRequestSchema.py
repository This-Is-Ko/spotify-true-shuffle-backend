from marshmallow import Schema, fields


class ShareLikedTracksRequestSchema(Schema):
    playlist_name = fields.String()
