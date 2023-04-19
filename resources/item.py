
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError

from flask_jwt_extended import jwt_required,get_jwt
from db import db
from models import ItemModel
from schemas import ItemSchema,ItemUpdateSchema

blp = Blueprint("Items",__name__,description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self,item_id):
        #Below will check in the db based on item_id as the primary key and if not exists then throws 404 error.
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self,item_id):
        jwt = get_jwt()
        #based on true or false specified in the app.py file
        if not jwt.get("is_admin"):
            abort(400,message="Admin access is required for delete")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message":"Item has been deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self,item_data,item_id): 
        #If the item doesn't exist it should be created or if it exists it should be updated.
        #Using put we need to exceute and idempotent request eg.running 1 or 10 requests should result in the same state at the end of it.
        item = ItemModel.query.get(item_id)
        if item:
            #Update since existing
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            #Create new
            item = ItemModel(id=item_id, **item_data)
        
        db.session.add(item)
        db.session.commit()
        return item

@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        #Defining instance of schemas so mentioning as many=True
        #Need to check why this is returned as list
        #return {"items":list(items.values())}
        #This will return a list and not an object with items
        return ItemModel.query.all()

    #This endpoint will require jwt tokens for creation of items
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):
        #item_data is passed from the schema as it is validated and then passed to the function hence below declaration is not required
        #item_data = request.get_json()
        #Below validation is for data existence
        # for item in items.values():
        #     if(
        #         item_data["name"] == item["name"]
        #         and item_data["store_id"] == item["store_id"]
        #     ):
        #         abort(400,message="Item already exists")
        # #name,price and store_id present in json
        # item_id = uuid.uuid4().hex
        # item = {**item_data,"id":item_id}
        # items[item_id] = item
        #The below validation is done in models file and also we are changing from dictionary file to Modelobject
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occured while inserting the item")

        return item