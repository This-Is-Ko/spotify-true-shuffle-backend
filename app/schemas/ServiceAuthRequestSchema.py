from marshmallow import Schema, fields


class ServiceAuthRequestSchema(Schema):
    client_id = fields.String(required=True)
    client_secret = fields.String(required=True)
