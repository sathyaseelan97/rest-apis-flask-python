from db import db

#mapping between a row in table to a Python class also objects

class ItemModel(db.Model):
    #Defining the table name and columns
    __tablename__ = "items"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),unique=True,nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2),unique=False,nullable=False)
    store_id = db.Column(db.Integer,db.ForeignKey("stores.id"), unique=False,nullable=False)
    #Fetch the store model object and create relationship
    #This back_populates will automatically populate the store variable with the store model object whose id matches with the foreign key
    #can be called like item.store    
    store = db.relationship("StoreModel",back_populates="items")
    tags = db.relationship("TagModel",back_populates="items",secondary="items_tags")