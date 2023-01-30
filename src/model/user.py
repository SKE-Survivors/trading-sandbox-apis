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
            "usdt": 500.0,
            "btc": 500.0,
            "eth": 0,
            "bnb": 0,
            "xrp": 0,
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

    def check_balance(self, token_symbol: str, amount: float):
        available = self.available_wallet()
        available_amount = available[token_symbol]
        return available_amount > 0 and available_amount >= amount


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
