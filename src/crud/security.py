import bcrypt

SECRET_KEY = "RARES_TALENT_BRIDGE"
ALGORITHM = "HS256"
ISSUER = "http://localhost:8000"
token_blacklist = {}

def hash_password(password: str) ->str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")