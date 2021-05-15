from flask_restful import Resource
from flask import request

from libs.strings import gettext
from models.item import ItemModel

# from models.order import OrderModel


class Order(Resource):
    @classmethod
    def post(cls):
        """Expect a token and a list of item ids from the request body.
        Construct an order and talk to the Strip API to make a charge.
        """
        data = request.get_json()  # token + list of item ids
        items = []

        # Iterate over items and retrive them from the database.
        for _id in data['item_ids']:
            item = ItemModel.find_by_id(_id)

            if not item:
                return {
                    'message': gettext('order_item_by_id_not_found').format(
                        id=_id,
                    ),
                }, 404

            items.append(item)

        order = OrderModel(items=items, status='pending')
        order.save_to_db()  # this does not submit to Stripe
