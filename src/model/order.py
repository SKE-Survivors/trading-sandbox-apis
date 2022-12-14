import datetime

from mongoengine import connect, Document, SequenceField, EmailField, DateTimeField, StringField, FloatField
from decouple import config


class Order(Document):
    id = SequenceField(primary_key=True)
    user_email = EmailField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now())
    status = StringField(required=True, max_length=10)
    type = StringField(required=True, max_length=5)
    pair_symbol = StringField(required=True, max_length=10)
    input_token = StringField(required=True, max_length=10)
    input_amount = FloatField(required=True, min_value=0)
    output_token = StringField(required=True, max_length=10)
    output_amount = FloatField(required=True, min_value=0)

    def info(self):
        return {
            "id": self.id,
            "user_email": self.user_email,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "type": self.type,
            "pair_symbol": self.pair_symbol,
            "input_token": self.input_token,
            "input_amount": self.input_amount,
            "output_token": self.output_token,
            "output_amount": self.output_amount,
        }

    # for user to call only
    def execute(self, user_email):
        if self.user_email != user_email:
            raise Exception(f"Order does not owned by user: {user_email}")

        self.update(status="finished")
        print(f"Executed order id: {self.id}, for user: {user_email}")

    # for user to call only
    def cancel(self, user_email):
        if self.user_email != user_email:
            raise Exception(f"Order does not owned by user: {user_email}")

        if self.status == "finished":
            raise Exception(f"Cancel not allow to finished order")

        self.update(status="cancel")
        print(f"Canceled order id: {self.id}, for user: {user_email}")


# ! temporary: tools to add sections
if __name__ == '__main__':
    connect(
        db=config('DB_NAME'),
        username=config('DB_USERNAME'),
        password=config('DB_PASSWORD'),
        host=config('DB_HOST'),
        authentication_source='admin',
        port=int(config('DB_PORT')),
    )

    Order(
        id=1,
        user_email="first@gmail.com",
        status="draft",
        type="buy",
        pair_symbol="btc-usdt",
        input_token="btc",
        input_amount=100,
        output_token="usdt",
        output_amount=30000,
    ).save()

    Order(
        user_email="first@gmail.com",
        status="active",
        type="sell",
        pair_symbol="eth-usdt",
        input_token="usdt",
        input_amount=99.5,
        output_token="eth",
        output_amount=5000,
    ).save()

    Order(
        user_email="first@gmail.com",
        status="finished",
        type="sell",
        pair_symbol="bnb-usdt",
        input_token="usdt",
        input_amount=10,
        output_token="bnb",
        output_amount=100,
    ).save()
