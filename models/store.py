from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),unique=True,nullable=False)
    #lazy=dynamic will not be done unless we till it to do so
    #cascade all will delete the items if the store is getting deleted 
    items = db.relationship("ItemModel",back_populates="store",lazy="dynamic",cascade="all, delete")
    tags = db.relationship("TagModel", back_populates="store",lazy="dynamic")