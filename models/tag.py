from db import db

class TagModel(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    #It would be better if name had to be unique within a store but two tags have the same name if their store id was different.
    #It is not possible in SQLAlchemy, we can do it manually by making unique=False and 
    #check that the store doesn't have tags with the same name.
    name = db.Column(db.String(80),unique=True,nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="tags")
    #By mentioning secondary SQLAlchemy will go through the secondary table in order to find what items this tag is related to
    #It will look at the tag.id foreign key that are linked to this tags table id
    items = db.relationship("ItemModel", back_populates="tags",secondary="items_tags")