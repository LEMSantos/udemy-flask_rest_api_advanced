from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from marshmallow import ValidationError
from flask_uploads import configure_uploads, patch_request_class

load_dotenv('.env', verbose=True)

from ma import ma
from db import db
from oa import oauth
from blocklist import BLOCKLIST
from resources.user import (
    UserRegister,
    UserLogin,
    User,
    TokenRefresh,
    UserLogout,
    SetPassword,
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar
from resources.github_login import GithubLogin, GithubAuthorize
from resources.order import Order
from libs.image_helper import IMAGE_SET

app = Flask(__name__)

app.config.from_object('default_config')
app.config.from_envvar('APPLICATION_SETTINGS')
patch_request_class(app, 10 * 1024 * 1024)  # 10MB max size upload
configure_uploads(app, IMAGE_SET)
api = Api(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(header, decrypted_token):
    return decrypted_token['jti'] in BLOCKLIST


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(Confirmation, '/user_confirmation/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<int:user_id>')
api.add_resource(ImageUpload, '/upload/image')
api.add_resource(AvatarUpload, '/upload/avatar')
api.add_resource(Image, '/image/<string:filename>')
api.add_resource(Avatar, '/avatar/<int:user_id>')
api.add_resource(GithubLogin, '/login/github')
api.add_resource(
    GithubAuthorize, '/login/github/authorized', endpoint='github.authorize'
)
api.add_resource(SetPassword, '/user/password')
api.add_resource(Order, '/order')

db.init_app(app)
ma.init_app(app)
oauth.init_app(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
