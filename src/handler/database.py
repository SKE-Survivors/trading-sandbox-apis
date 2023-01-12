from mongoengine import connect
from decouple import config
from model.user import User, Order, Trigger


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
        print("Connected to database")

    def add_user(self, email, username, password) -> User:
        user = User(
            email=email,
            username=username,
            password=password,
        ).save()
        print(f"Added user: {email}")
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

    def orders(self):
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
