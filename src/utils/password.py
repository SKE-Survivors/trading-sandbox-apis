import bcrypt

salt = bcrypt.gensalt()
encoding = 'utf-8'

def encode_pwd(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(encoding), salt)


def check_pwd(password: str, hashed_password: bytes) -> bool:
    return not bcrypt.checkpw(password.encode(encoding), hashed_password)