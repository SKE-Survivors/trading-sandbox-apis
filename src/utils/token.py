from decouple import config
from datetime import datetime

def create_token() -> str:
    timestamp = datetime.now().timestamp()
    secret = float(config('SECRET_NUMBER'))
    
    token = str(timestamp + secret).replace('.', '')
    return token
    