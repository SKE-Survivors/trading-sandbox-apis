from mongoengine import connect, Document, SequenceField, EmailField, IntField, StringField, FloatField
from decouple import config
from model.order import Order


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
            # todo: add order to redis
            
            order.update(status="active")

        # todo: remove trigger from redis
        
        print(f"Trigger id: {self.id}, has been trigger")
        return self.delete()

    def cancel(self, user_email):
        if self.user_email != user_email:
            raise Exception(f"Trigger does not owned by user: {user_email}")

        order = self.order()
        if order.status == "draft":
            order.delete()

        # todo: remove trigger from redis
        
        return self.delete()


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
