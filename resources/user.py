import os
from flask.views import MethodView
from flask import current_app
from flask_smorest import Blueprint,abort
#passlib hash library is used save password in different characters and numbers to store in the database
#pbkdf2_sha256 is a hashing algorithm
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt,get_jwt_identity
from blocklist import BLOCKLIST
from sqlalchemy import or_

from db import db
from models import UserModel
from schemas import UserSchema,UserRegisterSchema
from tasks import send_user_registration_email



blp = Blueprint("Users","users",description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        #for username exists below code can be skipped since we can add IntegrityError
        if UserModel.query.filter(
            or_(UserModel.username == user_data["username"],
            UserModel.email == user_data["email"])
            ).first():
            abort(409,message="Username or email already exists")
        #Password needs to be hashed before storing 
        user = UserModel(
            username=user_data["username"],
            email = user_data["email"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()
        #adding data to queue, passing email and username to send_user_registration_email function
        current_app.queue.enqueue(send_user_registration_email,user.email,user.username)
        return {"message":"User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self,user_data):
        #check if user exists and assign the same to user else it user will be None
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        #hashing the password that the user sent and comparing with the already hashed password present in database.
        #Unhashing the password present in database and comparing with the password sent by user is not done.
        if user and pbkdf2_sha256.verify(user_data["password"],user.password):
            #passing identity to the access_token to be stored in the access token
            #user_id will be present in the sub field of payload data in the JWT token
            #Refresh tokens are used for some important endpoints
            #Generating tokens in the background without inconveniencing the user.
            access_token = create_access_token(identity=user.id,fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return{"access_token":access_token,"refresh_token":refresh_token}
        abort(401,message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message":"Successfully logged out."}


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        # get_jwt_identity is the shortcut to get the sub field in the jwt which is the identity(i.e user.id)
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)
        return {"access_token":new_token}



@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200,UserSchema)
    def get(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"User Deleted successfully"},200
