import redis
from decouple import config
from utils import create_token

HASHNAME = "Session"


class SessionHandler:
    def __init__(self):
        self.client = redis.StrictRedis(
            host=config('REDISHOST'),
            port=config('REDISPORT'),
            db=config('REDISDB', 0),
        )
        print("Connected to redis")

    # login
    def set_session(self, email: str):
        if self.client.hexists(HASHNAME, email):
            self.remove_session(email)

        token = create_token()
        self.client.hset(HASHNAME, email, token)
        return token

    # check login session
    def in_session(self, email: str, token: str):
        return bytes(token, 'utf-8') == self.client.hget(HASHNAME, email)

    # logout
    def remove_session(self, email: str):
        self.client.hdel(HASHNAME, email)
