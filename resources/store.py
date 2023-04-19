import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort

from db import db
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError,IntegrityError

from schemas import StoreSchema

#Blueprint is used to divide an API in multiple segments.
#Methodview check

blp = Blueprint("stores",__name__,description = "Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200,StoreSchema)
    def get(self, store_id):
        #Below will fetch the store details based on the store_id
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    def delete(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message":"Store has been deleted."}
        raise NotImplementedError("Deleting a store is not implemented.")

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200,StoreSchema(many=True))
    def get(self):
        #return {"stores":list(stores.values())}
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201,StoreSchema())
    def post(self,store_data):
        #Validation for existence of store  
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            #Executes because of inconsistency in data. Ex.name
            abort(400,message="A store with the name already exists")
        except SQLAlchemyError:
            abort(500,message="An error occured while creating store")
        return store