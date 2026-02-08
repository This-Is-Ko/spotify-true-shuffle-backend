from marshmallow import Schema, fields, EXCLUDE
from schemas.UserAttributesRequestSchema import UserAttributesRequestSchema


class SaveUserRequestSchema(Schema):
    user_attributes = fields.Nested(UserAttributesRequestSchema)

    class Meta:
        unknown = EXCLUDE
