from mongoengine import connect, Document, SequenceField, EmailField, IntField, StringField, FloatField
from decouple import config
from model.order import Order
from handler.order import OrderHandler

oh = OrderHandler()

class Trigger(Document):
    id = SequenceField(primary_key=True)
    user_email = EmailField(required=True)
    order_id = IntField(required=True, min_value=1)
    pair_symbol = StringField(required=True, max_length=10)
    stop_price = FloatField(required=True, min_value=0)

    def info(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "order_id": self.order_id,
            "pair_symbol": self.pair_symbol,
            "stop_price": self.stop_price,
        }

    def order(self):
        return Order.objects.get(id=self.order_id)

    # for service to call only
    def trigger(self):
        order = self.order()
        if order.status == "draft":
            order.update(status="active")
            try:
                oh.add_order(order)
            except Exception as err:
                order.update(status="draft")
                raise err

        # todo: remove trigger from redis
        
        self.delete()
        print(f"Trigger id: {self.id}, has been trigger")

    def cancel(self):
        order = self.order()
        if order.status == "draft":
            order.delete()

        # todo: remove trigger from redis
        
        self.delete()
        print(f"Canceled trigger id: {self.id}, for user: {self.user_email}")
        


# ! temporary: tools to add sections
if __name__ == '__main__':
    connect(
        db=config('MONGODBNAME', 'trading-sandbox'),
        username=config('MONGOUSER'),
        password=config('MONGOPASSWORD'),
        host=config('MONGOHOST'),
        authentication_source='admin',
        port=int(config('MONGOPORT')),
    )

    Trigger(
        user_email="first@gmail.com",
        pair_symbol="btc-usdt",
        order_id=1,
        stop_price=100.9,
    ).save()
