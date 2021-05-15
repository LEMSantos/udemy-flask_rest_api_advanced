from collections import Counter
from flask_restful import Resource
from flask import request
from stripe import error

from libs.strings import gettext
from models.item import ItemModel
from models.order import OrderModel, ItemsInOrder
from schemas.order import OrderSchema

order_schema = OrderSchema()


class Order(Resource):
    @classmethod
    def post(cls):
        """Expect a token and a list of item ids from the request body.
        Construct an order and talk to the Strip API to make a charge.
        """
        data = request.get_json()  # token + list of item ids
        items = []
        item_id_quantities = Counter(data['item_ids'])

        # Iterate over items and retrive them from the database.
        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)

            if not item:
                return {
                    'message': gettext('order_item_by_id_not_found').format(
                        id=_id,
                    ),
                }, 404

            items.append(ItemsInOrder(item_id=_id, quantity=count))

        order = OrderModel(items=items, status='pending')
        order.save_to_db()  # this does not submit to Stripe

        try:
        order.set_status('failed')
        order.charge_with_stripe(data['token'])
        order.set_status('complete')

        return order_schema.dump(order)
        except error.CardError as e:
            return e.json_body, e.http_status
        except error.RateLimitError as e:
            return e.json_body, e.http_status
        except error.InvalidRequestError as e:
            return e.json_body, e.http_status
        except error.AuthenticationError as e:
            return e.json_body, e.http_status
        except error.APIConnectionError as e:
            return e.json_body, e.http_status
        except error.StripeError as e:
            return e.json_body, e.http_status
        except Exception as e:
            print(e)
            return {'message': gettext('order_error')}, 500
