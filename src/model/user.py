from mongoengine import connect, Document, StringField, EmailField, DictField, BinaryField
from decouple import config
from model.order import Order
from model.tigger import Tigger


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
            "orders": self.orders(),
        }

    def update(self, **kwargs):
        result = super().update(**kwargs)
        print(f"Updated [profile] user: {self.email}")
        return result

    def delete(self, signal_kwargs=None, **write_concern):
        result = super().delete(signal_kwargs, **write_concern)
        print(f"Deleted user: {self.email}")
        return result

    def orders(self):
        orders = []
        for order in Order.objects(user_email=self.email):
            orders.append(order.info())
        return orders

    def tiggers(self):
        tiggers = []
        for tigger in Tigger.objects(user_email=self.email):
            tigger.append(tigger.info())
        return tiggers


# ! temporary: just for testing
if __name__ == '__main__':
    connect(
        db=config('DB_NAME'),
        username=config('DB_USERNAME'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        authentication_source='admin',
        port=int(config('DB_PORT')),
    )

    User(
        email="first@gmail.com",
        username="username",
        password=b"password",
    ).save()
