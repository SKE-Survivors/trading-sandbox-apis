import redis
import pickle
from typing import List
from decouple import config
from model.trigger import Trigger

HASHNAME = "Matching::Trigger"


class TriggerHandler:
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

    def add_trigger(self, trigger: Trigger):
        hashname = self.create_hashname(trigger.pair_symbol, trigger.stop_price)

        if self.client.hexists(hashname, trigger.id):
            raise Exception("Duplicate trigger")

        # add trigger to redis
        pickled_trigger = pickle.dumps(trigger)
        self.client.hset(hashname, trigger.id, pickled_trigger)

    def get_triggers_at(self, pair_symbol: str, price: float) -> List[Trigger]:
        triggers: List[Trigger] = []
        hashname = self.create_hashname(pair_symbol, price)

        for pickled_trigger in self.client.hvals(hashname):
            triggers.append(pickle.loads(pickled_trigger))

        return triggers

    def remove_trigger(self, trigger: Trigger):
        hashname = self.create_hashname(trigger.pair_symbol, trigger.stop_price)

        self.client.hdel(hashname, trigger.id)
