from marshmallow import Schema, fields, EXCLUDE


class AuthCodeRequestSchema(Schema):
    code = fields.String(required=True)

    class Meta:
        unknown = EXCLUDE
