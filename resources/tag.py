from flask.views import MethodView
from flask_smorest import Blueprint,abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel,StoreModel,ItemModel
from schemas import TagSchema,TagAndItemSchema

#Blueprint is used to divide an API in multiple segments.
#Methodview check

blp = Blueprint("Tags","tags",__name__,description = "Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        #If needed to check the name and then add data , provided the unique = false for name field.
        # if TagModel.query.filter(TagModel.store_id == store_id,TagModel.name == tag_data["name"]).first():
        #     abort(400,message = "A tag with the same name already exists")

        #tag data will have the name
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,message=str(e))
        
        return tag

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagToItem(MethodView):
    #add a row(link) in items_tags or delete a row(unlink) from items_tags table
    #Check whether the items.store_id and tags.store_id are same and then perform link or unlink
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the tag.")
        
        return tag
    
    @blp.response(200, TagAndItemSchema)
    def delete(slef,item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while deleting the tag.")

        return {"message":"Item removed from tag","item":item,"tag":tag}                
    


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(202,description="Deletes a tag if no item is tagged to it.",example={"message":"Tag Deleted."})
    @blp.alt_response(404,description="Tag not found.")
    @blp.alt_response(400,description="Returned if the tag is assigned to one or more items. In this case tag is not deleted.")
    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag Deleted."}
        abort(400,message="Could not delete tag. Make sure tag is not associated with any items and then try again.")

        


