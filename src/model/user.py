from mongoengine import connect, Document, StringField, EmailField, DictField, BinaryField
from decouple import config
from model import Order, Trigger
from utils import map_pair

class User(Document):
    email = EmailField(primary_key=True, required=True)
    username = StringField(required=True, max_length=20)
    password = BinaryField(required=True)
    wallet = DictField(
        # todo: update default
        default={
            "usdt": 1000.0,
            "btc": 1000.0,
            "eth": 1000.0,
            "bnb": 1000.0,
        })

    def info(self):
        return {
            "email": self.email,
            "username": self.username,
            "password": self.password,
            "wallet": self.wallet,
        }

    def view(self):
        data = self.info()
        data.pop('password', None)
        data["available_wallet"] = self.available_wallet()
        data["orders"] = self.orders()
        data["triggers"] = self.triggers()
        return data

    def update(self, **kwargs):
        result = super().update(**kwargs)
        print(f"Updated [profile] user: {self.email}")
        return result

    def delete(self, signal_kwargs=None, **write_concern):
        result = super().delete(signal_kwargs, **write_concern)

        for order in Order.objects(user_email=self.email):
            order.delete()

        for trigger in Trigger.objects(user_email=self.email):
            trigger.delete()

        print(f"Deleted user: {self.email}")
        return result

    def orders(self):
        orders = []
        for order in Order.objects(user_email=self.email):
            orders.append(order.info())
        return orders

    def triggers(self):
        triggers = []
        for trigger in Trigger.objects(user_email=self.email):
            triggers.append(trigger.info())
        return triggers

    def available_wallet(self):
        active_status = ['active', 'draft']
        active_orders = list(filter(lambda d: d['status'] in active_status, self.orders()))

        available_wallet = self.wallet.copy()
        for order in active_orders:
            input_token, _ = map_pair(order["flag"], order["pair_symbol"])
            available_wallet[input_token] -= order['input_amount']

        return available_wallet

    def check_balance(self, token_symbol, amount):
        available = self.available_wallet()
        available_amount = available[token_symbol]
        return available_amount > 0 and available_amount >= amount

    def create_order(self, status, flag, pair_symbol, input_amount, output_amount) -> Order:
        if status.lower() not in ["finished", "active", "draft"]:
            raise Exception(f"Invalid status")
        
        if flag.lower() not in ["buy", "sell"]:
            raise Exception(f"Invalid flag")
        
        # check pair_symbol format
        input_token, _ = map_pair(flag, pair_symbol) 
        
        if not self.check_balance(input_token, input_amount):
            raise Exception(f"User balance not enough to create this order")
            
        order = Order(
            user_email=self.email,
            status=status.lower(),
            flag=flag.lower(),
            pair_symbol=pair_symbol.lower(),
            input_amount=input_amount,
            output_amount=output_amount,
        ).save()
        
        try:
            order.redis_add()
        except Exception as err:
            order.delete()
            raise err
        
        if order.status == "finished":
            try:
                self.execute_order(order)
            except Exception as err:
                order.delete()
                raise Exception(f"Execute order failed: {err}")        

        print(f"Added order id: {order.id}, for user: {self.email}")
        return order

    def execute_order(self, order: Order):
        if order.user_email != self.email:
            raise Exception(f"Order does not owned by user: {self.email}")
        
        order.execute()
        print(f"Executed order id: {order.id}, for user: {self.email}")

    def cancel_order(self, order: Order):
        if order.user_email != self.email:
            raise Exception(f"Order does not owned by user: {self.email}")
        
        order.cancel()
        print(f"Canceled order id: {order.id}, for user: {self.email}")

    def create_trigger(self, flag, pair_symbol, input_amount, output_amount, stop_price):
        order = self.create_order(
            status="draft",
            flag=flag,
            pair_symbol=pair_symbol,
            input_amount=input_amount,
            output_amount=output_amount,
        )

        try:
            trigger = Trigger(
                user_email=self.email,
                pair_symbol=pair_symbol,
                order_id=order.id,
                stop_price=stop_price,
            ).save()
        except Exception as err:
            order.delete()
            raise err
        
        try:
            trigger.redis_add()
        except Exception as err:
            trigger.delete()
            order.delete()
            raise err
            
        print(f"Added trigger id: {trigger.id}, for user: {self.email}")

    # delete trigger
    def cancel_trigger(self, trigger: Trigger):
        if trigger.user_email != self.email:
            raise Exception(f"Trigger does not owned by user: {self.email}")
        
        trigger.cancel()
        print(f"Canceled order id: {trigger.id}, for user: {self.email}")


# ! temporary: just for testing
if __name__ == '__main__':
    connect(
        db=config('MONGODBNAME', 'trading-sandbox'),
        username=config('MONGOUSER'),
        password=config('MONGOPASSWORD'),
        host=config('MONGOHOST'),
        authentication_source='admin',
        port=int(config('MONGOPORT')),
    )

    User(
        email="first@gmail.com",
        username="username",
        password=b"password",
    ).save()
