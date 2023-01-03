import datetime

from mongoengine import connect, Document, SequenceField, EmailField, DateTimeField, StringField, FloatField
from decouple import config
from model.user import User
from utils.map_pair_symbol import map_pair
from handler.order import OrderHandler

oh = OrderHandler()


class Order(Document):
    id = SequenceField(primary_key=True)
    user_email = EmailField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    status = StringField(required=True, max_length=10)
    flag = StringField(required=True, max_length=5)
    pair_symbol = StringField(required=True, max_length=10)
    input_amount = FloatField(required=True, min_value=0)
    output_amount = FloatField(required=True, min_value=0)

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
        return User.objects.get(email=self.user_email)

    def execute(self):
        if self.status == "draft":
            raise Exception(f"Draft order not allow to be execute")

        user = self.user()
        input_token, output_token = map_pair(self.flag, self.pair_symbol)

        user.wallet[input_token] -= self.input_amount
        user.wallet[output_token] += self.output_amount
        user.save()

        try:
            oh.remove_order(self)
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
            oh.remove_order(self)
        except Exception as err:
            self.update(status="active")
            raise err

        print(f"Canceled order id: {self.id}, for user: {self.user_email}")


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
