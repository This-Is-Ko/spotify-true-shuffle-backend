from marshmallow import Schema, fields
from schemas.UserAttributesRequestSchema import UserAttributesRequestSchema


class SaveUserRequestSchema(Schema):
    user_attributes = fields.Nested(UserAttributesRequestSchema)
