import datetime
from mongoengine import connect, Document, SequenceField, EmailField, DateTimeField, StringField, FloatField
from decouple import config


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

    def price(self) -> float:
        return self.input_amount / self.output_amount if self.flag == "buy" else self.output_amount / self.input_amount

    def update(self, **kwargs):
        if self.status == "finished":
            raise Exception("Finished order does not allows to update")

        return super().update(**kwargs)


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
