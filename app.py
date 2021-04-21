from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from ma import ma
from db import db
from blocklist import BLOCKLIST
from resources.user import (
    UserRegister,
    UserLogin,
    User,
    TokenRefresh,
    UserLogout,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLOCKLIST_ENABLED'] = True
app.config['JWT_BLOCKLIST_TOKEN_CHECKS'] = [
    'access',
    'refresh',
]
app.secret_key = 'ffeecf2d-db82-48e1-a4ce-5442e5d95b41'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(header, decrypted_token):
    return decrypted_token['jti'] in BLOCKLIST


api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    db.init_app(app)
    ma.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
