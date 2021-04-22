from flask_restful import Resource
from models.store import StoreModel

NAME_ALREADY_EXISTS = 'A store with name "{name}" already exists.'
ERROR_INSERTING = 'An error occurred while inserting the store.'
STORE_NOT_FOUND = 'Store not found.'
STORE_DELETED = 'Store deleted.'


class Store(Resource):
    @classmethod
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {'message': STORE_NOT_FOUND}, 404

    @classmethod
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {
                'message': NAME_ALREADY_EXISTS.format(name=name),
            }, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {
                'message': ERROR_INSERTING,
            }, 500

        return store.json(), 201

    @classmethod
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {'message': STORE_DELETED}


class StoreList(Resource):
    @classmethod
    def get(cls):
        return {'stores': [x.json() for x in StoreModel.find_all()]}
