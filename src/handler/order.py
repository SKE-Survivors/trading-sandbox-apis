import datetime
import redis
import pickle
from typing import List, Tuple
from decouple import config
from model.order import Order

HASHNAME = "Matching::Order"


class OrderHandler:
    def __init__(self):
        self.client = redis.StrictRedis(
            host=config('REDISHOST'),
            port=config('REDISPORT'),
            username=config('REDISUSER', None),
            password=config('REDISPASSWORD', None),
            db=config('REDISDB', 0),
        )

    def create_hashname(self, pair_symbol, price):
        return "::".join([HASHNAME, pair_symbol, price])

    def add_order(self, order: Order):
        price = order.input_amount / order.output_amount if order.flag == "buy" else order.output_amount / order.input_amount
        hashname = self.create_hashname(order.pair_symbol, price)

        if self.client.hexists(hashname, order.id):
            raise Exception("Duplicate order")

        # add order to redis
        pickled_order = pickle.dumps(order)
        self.client.hset(hashname, order.id, pickled_order)

        # check execution
        if self.should_be_update(order.pair_symbol, price):
            self.update(order.pair_symbol, price)

    def should_be_update(self, pair_symbol: str, price: float):
        orders = self.get_orders_at(pair_symbol, price)
        result = {"ask-size": 0, "bid-size": 0}

        for order in orders:
            if order.flag == "buy":
                result['bid-size'] += order.output_amount
            if order.flag == "sell":
                result['ask-size'] += order.input_amount

        return result['bid-size'] != 0 and result['ask-size'] != 0

    def update(self, pair_symbol: str, price: float):
        if not self.should_be_update(pair_symbol, price):
            return

        orders = self.get_orders_at(pair_symbol, price)
        orders.sort(key=lambda o: o.timestamp, reverse=False)

        buy_orders: List[Order] = []
        sell_orders: List[Order] = []

        for order in orders:
            if order.flag == "buy":
                buy_orders.append(order)
            else:
                sell_orders.append(order)

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
        self.add_order(base)

        sub.execute()
        self.update(pair_symbol, price)

    def get_orders_at(self, pair_symbol: str, price: float) -> List[Order]:
        orders: List[Order] = []
        hashname = self.create_hashname(pair_symbol, price)

        for pickled_order in self.client.hvals(hashname):
            orders.append(pickle.loads(pickled_order))

        return orders

    def remove_order(self, order: Order):
        price = order.input_amount / order.output_amount if order.flag == "buy" else order.output_amount / order.input_amount
        hashname = self.create_hashname(order.pair_symbol, price)

        self.client.hdel(hashname, order.id)
