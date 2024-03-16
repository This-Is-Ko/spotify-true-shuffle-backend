from marshmallow import Schema, fields


class AuthCodeRequestSchema(Schema):
    code = fields.String(required=True)
