from sqlalchemy.orm import load_only
from ma import ma
from models.order import OrderModel


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderModel
        load_only = ('token',)
        dump_only = ('id', 'status')
        include_fk = True
        load_instance = True
