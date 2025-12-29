import uuid
import bcrypt
import jwt
import datetime

SECRET_KEY = "RARES_TALENT_BRIDGE"
ALGORITHM = "HS256"
ISSUER = "http://localhost:8000"
token_blacklist = {}

def hash_password(password: str) ->str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(password_clara: str, password_din_db: str) -> bool:
    return bcrypt.checkpw(
        password_clara.encode('utf-8'),
        password_din_db.encode('utf-8')
    )

def create_jws_token(user_id: int, role: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "iss": ISSUER,
        "sub":str (user_id),
        "exp": now + datetime.timedelta(minutes=60),
        "jti": str(uuid.uuid4()),
        "role": role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)