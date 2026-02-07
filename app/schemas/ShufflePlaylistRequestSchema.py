from marshmallow import Schema, fields

from classes.shuffle_type import Shuffle_Type


class ShufflePlaylistRequestSchema(Schema):
    playlist_id = fields.String(required=True)
    playlist_name = fields.String(required=True)
    shuffle_type = fields.Enum(Shuffle_Type, by_value=True, required=False,)
