from marshmallow import Schema, fields, EXCLUDE


class ShareLikedTracksRequestSchema(Schema):
    playlist_name = fields.String()

    class Meta:
        unknown = EXCLUDE
