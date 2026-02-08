from marshmallow import Schema, fields, EXCLUDE


class UserAttributesRequestSchema(Schema):
    trackers_enabled = fields.Boolean(required=True)

    class Meta:
        unknown = EXCLUDE
