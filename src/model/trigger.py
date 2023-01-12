import redis
import pickle
from typing import List
from mongoengine import connect, Document, SequenceField, EmailField, IntField, StringField, FloatField
from decouple import config
from model import Order


class Trigger(Document):
    id = SequenceField(primary_key=True)
    user_email = EmailField(required=True)
    order_id = IntField(required=True, min_value=1)
    pair_symbol = StringField(required=True, max_length=10)
    stop_price = FloatField(required=True, min_value=0)

    redis_client = redis.StrictRedis(
        host=config('REDISHOST'),
        port=config('REDISPORT'),
        username=config('REDISUSER', None),
        password=config('REDISPASSWORD', None),
        db=config('REDISDB', 0),
    )

    def info(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "order_id": self.order_id,
            "pair_symbol": self.pair_symbol,
            "stop_price": self.stop_price,
        }

    def order(self) -> Order:
        return Order.objects.get(id=self.order_id)

    # for service to call only
    def trigger(self):
        order = self.order()
        if order.status == "draft":
            order.update(status="active")
            try:
                order.redis_add()
            except Exception as err:
                order.update(status="draft")
                raise err

        # todo: check rollback
        self.redis_remove()
        self.delete()
        print(f"Trigger id: {self.id}, has been trigger")

    def cancel(self):
        order = self.order()
        if order.status == "draft":
            order.delete()

        # todo: check rollback
        self.redis_remove()
        self.delete()
        print(f"Canceled trigger id: {self.id}, for user: {self.user_email}")

    @classmethod
    def redis_hashname(cls, pair_symbol: str, price: float) -> str:
        return "::".join(["Matching::Trigger", pair_symbol, price])

    def redis_remove(self):
        hashname = Trigger.redis_hashname(self.pair_symbol, self.stop_price)
        self.redis_client.hdel(hashname, self.id)

    def redis_add(self):
        hashname = Trigger.redis_hashname(self.pair_symbol, self.stop_price)

        if self.redis_client.hexists(hashname, self.id):
            raise Exception("Duplicate trigger")

        # add trigger to redis
        pickled_trigger = pickle.dumps(self)
        self.redis_client.hset(hashname, self.id, pickled_trigger)

    @classmethod
    def redis_get_at(cls, pair_symbol: str, price: float):
        triggers: List[cls] = []
        hashname = cls.redis_hashname(pair_symbol, price)

        for pickled_trigger in cls.redis_client.hvals(hashname):
            triggers.append(pickle.loads(pickled_trigger))

        return triggers


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
