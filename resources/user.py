from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from models.user import UserModel
from blacklist import BLACKLIST

USERNAME_ALREADY_EXISTS = 'A user with that username already exists.'
BLANK_ERROR = '"{field}" cannot be left blank.'
USER_NOT_FOUND = 'User not found.'
USER_DELETED = 'User deleted.'
USER_CREATED = 'User created successfully.'
INVALID_CREDENTIALS = 'Invalid credentials.'
USER_LOGGED_OUT = 'User <id={id}> successfully logged out.'


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    'username',
    type=str,
    required=True,
    help=BLANK_ERROR.format(field='username'),
)
_user_parser.add_argument(
    'password',
    type=str,
    required=True,
    help=BLANK_ERROR.format(field='password'),
)


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {
                'message': USERNAME_ALREADY_EXISTS,
            }, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {'message': USER_DELETED}, 200


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
            }, 200

        return {'message': INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {
            'message': USER_LOGGED_OUT.format(id=user_id),
        }, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
