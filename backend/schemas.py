from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class AccountSchema(Schema):
    account_number = fields.String(required=True)
    account_type = fields.String(required=True)
    balance = fields.Float(required=False)

class TransactionSchema(Schema):
    from_account_id = fields.Integer(required=True)
    to_account_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
