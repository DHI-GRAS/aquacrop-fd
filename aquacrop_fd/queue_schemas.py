from marshmallow import Schema, fields, validate


class GeometrySchema(Schema):
    coordinates = fields.List(fields.List(fields.List(fields.Float)))
    type = fields.String(validate.OneOf(['Polygon']))


class JobSchema(Schema):
    guid = fields.UUID(required=True)
    area_name = fields.String(required=True)
    crop = fields.String(required=True)
    planting_date = fields.Date(format="%Y-%m-%d")
    irrigated = fields.Boolean(required=True)
    fraction = fields.Float(required=True)
    geometry = fields.Nested(GeometrySchema, required=True)


class DoneSchema(Schema):
    guid = fields.UUID(required=True)
    error = fields.String(required=True, allow_none=True)
