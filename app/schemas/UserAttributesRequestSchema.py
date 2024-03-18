from marshmallow import Schema, fields


class UserAttributesRequestSchema(Schema):
    trackers_enabled = fields.Boolean(required=True)
