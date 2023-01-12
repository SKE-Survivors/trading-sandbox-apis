import datetime
import redis
import pickle
from typing import List
from mongoengine import connect, Document, SequenceField, EmailField, DateTimeField, StringField, FloatField
from decouple import config
from utils.map_pair_symbol import map_pair


class Order(Document):
    id = SequenceField(primary_key=True)
    user_email = EmailField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    status = StringField(required=True, max_length=10)
    flag = StringField(required=True, max_length=5)
    pair_symbol = StringField(required=True, max_length=10)
    input_amount = FloatField(required=True, min_value=0)
    output_amount = FloatField(required=True, min_value=0)

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
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "flag": self.flag,
            "pair_symbol": self.pair_symbol,
            "input_amount": self.input_amount,
            "output_amount": self.output_amount,
        }

    def user(self):
        # todo: return User (use in `execute()`)

    def execute(self):
        if self.status == "draft":
            raise Exception(f"Draft order not allow to be execute")

        user = self.user()
        input_token, output_token = map_pair(self.flag, self.pair_symbol)

        user.wallet[input_token] -= self.input_amount
        user.wallet[output_token] += self.output_amount
        user.save()

        try:
            self.redis_remove()
        except Exception as err:
            user.wallet[input_token] += self.input_amount
            user.wallet[output_token] -= self.output_amount
            user.save()
            raise err

        self.update(status="finished")
        print(f"Executed order id: {self.id}, for user: {self.user_email}")

    def cancel(self):
        if self.status == "finished":
            raise Exception(f"Cancel not allow to finished order")

        self.update(status="cancel")

        try:
            self.redis_remove()
        except Exception as err:
            self.update(status="active")
            raise err

        print(f"Canceled order id: {self.id}, for user: {self.user_email}")

    def price(self) -> float:
        return self.input_amount / self.output_amount if self.flag == "buy" else self.output_amount / self.input_amount

    @classmethod
    def redis_hashname(cls, pair_symbol: str, price: float) -> str:
        return "::".join(["Matching::Order", pair_symbol, price])

    def redis_remove(self):
        hashname = Order.redis_hashname(self.pair_symbol, self.price())
        self.redis_client.hdel(hashname, self.id)

    def redis_add(self):
        price = self.price()
        hashname = Order.redis_hashname(self.pair_symbol, price)

        if self.redis_client.hexists(hashname, self.id):
            self.remove_order()

        # add order to redis
        pickled_order = pickle.dumps(self)
        self.redis_client.hset(hashname, self.id, pickled_order)

        # check execution
        Order.redis_update(self.pair_symbol, price)

    @classmethod
    def redis_get_at(cls, pair_symbol: str, price: float):
        orders: List[cls] = []
        hashname = cls.redis_hashname(pair_symbol, price)

        for pickled_order in cls.redis_client.hvals(hashname):
            orders.append(pickle.loads(pickled_order))

        return orders

    @classmethod
    def redis_should_be_update(cls, pair_symbol: str, price: float):
        orders = cls.redis_get_at(pair_symbol, price)
        result = {"ask-size": 0, "bid-size": 0}

        for order in orders:
            if order.flag == "buy":
                result['bid-size'] += order.output_amount
            if order.flag == "sell":
                result['ask-size'] += order.input_amount

        return result['bid-size'] != 0 and result['ask-size'] != 0

    @classmethod
    def redis_update(cls, pair_symbol: str, price: float):
        if not cls.redis_should_be_update(pair_symbol, price):
            return

        orders = cls.redis_get_at(pair_symbol, price)
        orders.sort(key=lambda o: o.timestamp, reverse=False)

        buy_orders: List[cls] = filter(lambda o: o.flag == "buy", orders)
        sell_orders: List[cls] = filter(lambda o: o.flag == "sell", orders)

        # update redis
        if buy_orders[0].output_amount > sell_orders[0].input_amount:
            base = buy_orders[0]
            sub = sell_orders[0]
        else:
            sub = buy_orders[0]
            base = sell_orders[0]

        base.input_amount -= sub.output_amount
        base.output_amount -= sub.input_amount
        base.save()
        base.redis_add()

        sub.execute()
        cls.redis_update(pair_symbol, price)


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

    Order(
        id=1,
        user_email="first@gmail.com",
        status="draft",
        flag="buy",
        pair_symbol="btc-usdt",
        input_amount=100,
        output_amount=30000,
    ).save()

    Order(
        user_email="first@gmail.com",
        status="active",
        flag="sell",
        pair_symbol="eth-usdt",
        input_amount=99.5,
        output_amount=5000,
    ).save()

    Order(
        user_email="first@gmail.com",
        status="finished",
        flag="sell",
        pair_symbol="bnb-usdt",
        input_amount=10,
        output_amount=100,
    ).save()
