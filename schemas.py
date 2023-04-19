from marshmallow import Schema,fields

#Whenever we create an itemmodel or Storemodel it is going to have an nested object Itemmo will have nested storemo and the vice-versa
#So we have to update schemas to reflect that only in certain cases.

#This file is to define scehmas for data validation
class PlainItemSchema(Schema):
    #id field is to be returned as part of the api hence it has to be dump_only true, other fields are required true
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    name = fields.Str(required=True)
    id = fields.Int(dump_only=True)

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class ItemUpdateSchema(Schema):
    #name or price,store_id can be given by the user so no parameters are need to be mentioned
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True,load_only=True)
    #Relationship also has to be mentioned in the schema
    #This will only be used when returning data to the client and not while receiving
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema(),dump_only=True))

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema(),dump_only=True))
    tags = fields.List(fields.Nested(PlainTagSchema(),dump_only=True))

class TagSchema(PlainTagSchema):
    #Removing required=True
    store_id = fields.Int(load_only=True)
    #Relationship also has to be mentioned in the schema
    #This will only be used when returning data to the client and not while receiving
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema(),dump_only=True))

class TagAndItemSchema(Schema):
    #This schema is intended to return the tag and item that are related
    message = fields.Str()
    item = fields.Nested(PlainItemSchema)
    tag = fields.Nested(PlainTagSchema)

class UserSchema(Schema):
    #dump_only=True is given for fields which are not received from the users.
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    #load_only=True is given for fields which are not to be returned when the API is called
    #Also the password should never be sent to the user
    password = fields.Str(required=True,load_only=True)