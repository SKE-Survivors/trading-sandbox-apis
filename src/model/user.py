from mongoengine import connect, Document, StringField, EmailField, DictField, BinaryField
from decouple import config
from model.order import Order
from model.trigger import Trigger


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
        active_orders = list(
            filter(lambda d: d['status'] in active_status, self.orders()))

        available_wallet = self.wallet.copy()
        for order in active_orders:
            available_wallet[order['input_token']] -= order['input_amount']
            
        return available_wallet

    def check_balance(self, token_symbol, amount):
        available = self.available_wallet()
        available_amount = available[token_symbol]
        return available_amount > 0 and available_amount >= amount

    def create_order(self, status, type, pair_symbol, input_token,
                     input_amount, output_token, output_amount) -> Order:
        order = Order(
            user_email=self.email,
            status=status.lower(),
            type=type.lower(),
            pair_symbol=pair_symbol.lower(),
            input_token=input_token.lower(),
            input_amount=input_amount,
            output_token=output_token.lower(),
            output_amount=output_amount,
        ).save()

        print(f"Added order id: {order.id}, for user: {self.email}")
        return order

    def execute_order(self, order: Order):
        order.execute(self.email)
        self.wallet[order.input_token] -= order.input_amount
        self.wallet[order.output_token] += order.output_amount
        self.save()
        print(f"Executed order id: {order.id}, for user: {self.email}")

    def cancel_order(self, order: Order):
        order.cancel(self.email)
        print(f"Canceled order id: {order.id}, for user: {self.email}")

    def create_trigger(self, type, pair_symbol, input_token, input_amount,
                       output_token, stop_price, limit_price):
        order = self.create_order(status="draft",
                                  type=type,
                                  pair_symbol=pair_symbol,
                                  input_token=input_token,
                                  input_amount=input_amount,
                                  output_token=output_token,
                                  output_amount=input_amount *
                                  limit_price).save()

        trigger = Trigger(
            user_email=self.email,
            pair_symbol=pair_symbol,
            output_token=output_token,
            order_id=order.id,
            stop_price=stop_price,
        ).save()
        print(f"Added trigger id: {trigger.id}, for user: {self.email}")

    # this mean delete trigger
    def cancel_trigger(self, trigger: Trigger):
        trigger.cancel(self.email)
        print(f"Canceled order id: {trigger.id}, for user: {self.email}")


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
