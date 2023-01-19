import pickle
import redis
from mongoengine import connect
from typing import List
from decouple import config
from model.user import User, Order, Trigger
from utils.map_pair_symbol import map_pair


class DatabaseHandler:
    def __init__(self):
        connect(
            db=config('MONGODBNAME', 'trading-sandbox'),
            username=config('MONGOUSER'),
            password=config('MONGOPASSWORD'),
            host=config('MONGOHOST'),
            authentication_source='admin',
            port=int(config('MONGOPORT')),
        )
        self.client = redis.StrictRedis(
            host=config('REDISHOST'),
            port=config('REDISPORT'),
            username=config('REDISUSER', None),
            password=config('REDISPASSWORD', None),
            db=config('REDISDB', 0),
        )
        print("Connected to database")

    # Database | Basic

    def create_user(self, email, username, password) -> User:
        user = User(
            email=email,
            username=username,
            password=password,
        ).save()
        print(f"Created user: {email}")
        return user

    def find_user(self, email) -> User:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        return user

    def find_order(self, id) -> Order:
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            order = None
        return order

    def find_all_orders(self):
        orders = []
        for order in Order.objects():
            orders.append(order.info())
        return orders

    def find_trigger(self, id) -> Trigger:
        try:
            trigger = Trigger.objects.get(id=id)
        except Trigger.DoesNotExist:
            trigger = None
        return trigger

    # Database | Execution | User

    def delete_user(self, user: User):
        for order in Order.objects(user_email=user.email):
            self.redis_order_remove(order)
            order.delete()

        for trigger in Trigger.objects(user_email=user.email):
            self.redis_trigger_remove(trigger)
            trigger.delete()

        user.delete()
        print(f"Deleted user: {user.email}")

    # Database | Execution | Order

    def create_order(self, user: User, status, flag, pair_symbol, input_amount, output_amount) -> Order:
        if status.lower() not in ["finished", "active", "draft"]:
            raise Exception(f"Invalid status")

        if flag.lower() not in ["buy", "sell"]:
            raise Exception(f"Invalid flag")

        # check pair_symbol format
        input_token, _ = map_pair(flag, pair_symbol)

        if not user.check_balance(input_token, input_amount):
            raise Exception(f"User balance not enough to create this order")

        order = Order(
            user_email=user.email,
            status=status.lower(),
            flag=flag.lower(),
            pair_symbol=pair_symbol.lower(),
            input_amount=input_amount,
            output_amount=output_amount,
        ).save()

        if order.status == "finished":
            try:
                self.execute(order.id)
            except Exception as err:
                order.delete()
                raise Exception(f"Execute order failed: {err}")
            print(
                f"Created and Executed order id: {order.id}, for user: {user.email}"
            )
        else:
            print(f"Created order id: {order.id}, for user: {user.email}")
            try:
                self.redis_order_add(order)
            except Exception as err:
                order.delete()
                print(f"Delete order id: {order.id}, due to: {err}")
                raise Exception(f"Add order to redis failed: {err}")
        return order

    def execute(self, order_id: int, user: User = None):
        order = self.find_order(order_id)

        if order.status == "draft":
            raise Exception(f"Draft order not allow to be execute")

        if user:
            if order.user_email != user.email:
                raise Exception(f"Order does not owned by user: {user.email}")
        else:
            user = self.find_user(order.user_email)

        input_token, output_token = map_pair(order.flag, order.pair_symbol)

        user.wallet[input_token] -= order.input_amount
        user.wallet[output_token] += order.output_amount
        user.save()

        try:
            self.redis_order_remove(order)
        except Exception as err:
            user.wallet[input_token] += order.input_amount
            user.wallet[output_token] -= order.output_amount
            user.save()
            raise Exception(f"Remove order from redis failed: {err}")

        if order.status != "finished":
            order.update(status="finished")
            print(
                f"Executed order id: {order.id}, for user: {order.user_email}")

    def cancel_order(self, order: Order, user: User = None):
        if user and order.user_email != user.email:
            raise Exception(f"Order does not owned by user: {user.email}")

        old_status = order.status

        if old_status == "finished":
            raise Exception(f"Cancel not allow to finished order")

        order.update(status="cancel")

        try:
            self.redis_order_remove(order)
        except Exception as err:
            order.update(status=old_status)
            raise Exception(f"Add trigger to redis failed: {err}")

        print(f"Canceled order id: {order.id}, for user: {order.user_email}")

    # Database | Execution | Trigger

    def create_trigger(self, user: User, flag, pair_symbol, input_amount, output_amount, stop_price) -> Trigger:
        order = self.create_order(user, "draft", flag, pair_symbol, input_amount, output_amount)

        try:
            trigger = Trigger(
                user_email=user.email,
                pair_symbol=pair_symbol,
                order_id=order.id,
                stop_price=stop_price,
            ).save()
        except Exception as err:
            order.delete()
            raise Exception(f"Save trigger failed: {err}")

        try:
            self.redis_trigger_add(trigger)
        except Exception as err:
            trigger.delete()
            order.delete()
            raise Exception(f"Add trigger to redis failed: {err}")

        print(f"Added trigger id: {trigger.id}, for user: {user.email}")
        return trigger

    def trigger(self, trigger: Trigger):
        order = trigger.order()
        if order.status == "draft":
            order.update(status="active")
            try:
                self.redis_order_add(order)
            except Exception as err:
                order.update(status="draft")
                raise Exception(f"Add order to redis failed: {err}")

        # todo: check rollback
        self.redis_trigger_remove(trigger)
        trigger.delete()
        print(f"Trigger id: {trigger.id}, has been trigger")

    def cancel_trigger(self, trigger: Trigger, user: User = None):
        if user and trigger.user_email != user.email:
            raise Exception(f"Trigger does not owned by user: {user.email}")

        order = trigger.order()
        if order.status == "draft":
            order.delete()

        # todo: check rollback
        self.redis_trigger_remove(trigger)
        trigger.delete()
        print(
            f"Canceled trigger id: {trigger.id}, for user: {trigger.user_email}"
        )

    # Redis | Order

    def redis_order_hashname(self, pair_symbol: str, price: float) -> str:
        return "::".join(["Matching::Order", pair_symbol, str(price)])

    def redis_order_remove(self, order: Order):
        hashname = self.redis_order_hashname(order.pair_symbol, order.price())
        try:
            self.client.hdel(hashname, order.id)
        except:
            pass  # skip if order doesn't exist

    def redis_order_add(self, order: Order):
        hashname = self.redis_order_hashname(order.pair_symbol, order.price())

        if self.client.hexists(hashname, order.id):
            self.redis_order_remove(order)

        # add order to redis
        pickled_order = pickle.dumps(order)
        self.client.hset(hashname, order.id, pickled_order)

        # check execution
        try:
            self.redis_matching_order(order.pair_symbol, order.price())
        except Exception as err:
            raise Exception(f"Matching failed: {err}")

    def redis_get_orders_at(self, pair_symbol: str, price: float) -> List[Order]:
        orders: List[Order] = []
        hashname = self.redis_order_hashname(pair_symbol, price)

        for pickled_order in self.client.hvals(hashname):
            orders.append(pickle.loads(pickled_order))

        return orders

    def redis_order_should_update(self, pair_symbol: str, price: float) -> bool:
        orders = self.redis_get_orders_at(pair_symbol, price)
        result = {"ask-size": 0, "bid-size": 0}

        for order in orders:
            if order.flag == "buy":
                result['bid-size'] += order.output_amount
            if order.flag == "sell":
                result['ask-size'] += order.input_amount

        return result['bid-size'] != 0 and result['ask-size'] != 0

    def redis_matching_order(self, pair_symbol: str, price: float):
        if not self.redis_order_should_update(pair_symbol, price):
            return

        orders = self.redis_get_orders_at(pair_symbol, price)
        orders.sort(key=lambda o: o.timestamp, reverse=False)

        buy_orders: List[self] = list(filter(lambda o: o.flag == "buy", orders))
        sell_orders: List[self] = list(
            filter(lambda o: o.flag == "sell", orders))

        # update redis
        if buy_orders[0].output_amount > sell_orders[0].input_amount:
            base: Order = buy_orders[0]
            sub: Order = sell_orders[0]
        else:
            sub: Order = buy_orders[0]
            base: Order = sell_orders[0]

        # todo: add rollback

        self.execute(sub.id)

        if base.input_amount - sub.output_amount != 0:
            # execute partial_base
            base_user = self.find_user(base.user_email)
            self.create_order(base_user, "finished", base.flag,
                              base.pair_symbol, sub.output_amount,
                              sub.input_amount)

            # update base
            base_order = self.find_order(base.id)
            base_order.input_amount -= sub.output_amount
            base_order.output_amount -= sub.input_amount
            base_order.save()
            self.redis_order_add(base_order)
        else:
            self.execute(base.id)

        self.redis_matching_order(pair_symbol, price)

    # Redis | Trigger

    def redis_trigger_hashname(self, pair_symbol: str, price: float) -> str:
        return "::".join(["Matching::Trigger", pair_symbol, price])

    def redis_trigger_remove(self, trigger: Trigger):
        hashname = self.redis_trigger_hashname(trigger.pair_symbol, trigger.stop_price)
        self.client.hdel(hashname, trigger.id)

    def redis_trigger_add(self, trigger: Trigger):
        hashname = self.redis_trigger_hashname(trigger.pair_symbol, trigger.stop_price)

        if self.client.hexists(hashname, trigger.id):
            raise Exception("Duplicate trigger")

        # add trigger to redis
        pickled_trigger = pickle.dumps(trigger)
        self.client.hset(hashname, trigger.id, pickled_trigger)

    def redis_get_triggers_at(self, pair_symbol: str, price: float) -> List[Trigger]:
        triggers: List[Trigger] = []
        hashname = self.redis_trigger_hashname(pair_symbol, price)

        for pickled_trigger in self.client.hvals(hashname):
            triggers.append(pickle.loads(pickled_trigger))

        return triggers
