from mongoengine import connect
from decouple import config
from model.user import User


class DatabaseHandler:
    def __init__(self):
        connect(
            db=config('DB_NAME'),
            username=config('DB_USERNAME'),
            password=config('DB_PASSWORD'),
            host=config('DB_HOST'),
            authentication_source='admin',
            port=int(config('DB_PORT')),
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
