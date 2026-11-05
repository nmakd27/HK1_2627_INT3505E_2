from marshmallow import Schema, fields, validate

class OrderItemIn(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

class OrderIn(Schema):
    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    items = fields.List(fields.Nested(OrderItemIn), required=True, validate=validate.Length(min=1))

class OrderItemOut(Schema):
    id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()
    unit_price_cents = fields.Int()

class OrderOut(Schema):
    id = fields.Int()
    customer_name = fields.Str()
    created_at = fields.DateTime()
    items = fields.List(fields.Nested(OrderItemOut))