import os 
import redis
from flask import Flask,jsonify

#connects the flask-smorest extension to flask app
from flask_smorest import Api

from db import db
import models

from rq import Queue
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from blocklist import BLOCKLIST
from dotenv import load_dotenv


#import models need to be done before the SQL Alchemy extension because the models consists of the table structure

def create_app(db_url=None):
    app = Flask(__name__)
    #Loading the environment variables for database url
    load_dotenv()
    #Defining queue connection and setting up queues
    connection = redis.from_url(os.getenv("REDIS_URL"))
    #"emails" is the name of the queue 
    app.queue = Queue("emails",connection=connection)
    #Registering blueprints with api
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    #Tells flask-smorest to use the swagger-ui documentation
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" 
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    #Track modifications will slower the sqlalchemy and not necessary
    #This initializes the flask sqlalchemy extension which gives the flask app so it can connect flask app 
        
    #The JWT secret keys are used for signing the JWTs
    #Secret keys should be kept safe and it would be a long.random value
    #app.config["JWT_SECRET_KEY"] = "Test"
    #long random secret key
    #secrets.SystemRandom().getrandbits(128)
    app.config["JWT_SECRET_KEY"] = "323519564080472983615573373243762478919"
    db.init_app(app) 
    migrate = Migrate(app,db)


    jwt = JWTManager(app)
    
    @jwt.token_in_blocklist_loader
    #When we receive a JWT this function runs and checks whether the token is in blocklist or not.
    #jti is the JWT's unique identifier
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return(
            jsonify({"description":"Token has been revoked","error":"token_revoked"}),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):
        return(
            jsonify({"description":"Token is not fresh","error":"fresh_token_required"}),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        #Instead of verifying the admin here we should check in the database whether is the user is admin or not.
        """This function will be called everytime the jwt is created and also used to add information to the jwt token"""
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}
    #adding error handling for jwt exceptions
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        #This function returns a tuple
        return (jsonify({"description":"The token has expired.","error":"Token expired"}),
        401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"description":"Signature verification failed","error":"Token invalid"}),
        401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"description":"Request does not contain an access token","error":"authorization_required"}),
        401
        )


    # @app.before_first_request
    # def create_tables():
    #     db.create_all()
    #Alternate for the above lines
    
    # with app.app_context():
    #     db.create_all()

    api = Api(app)

    #registering the blueprints
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    
    return app
