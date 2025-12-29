import uuid
import bcrypt
import jwt
import datetime

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

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

def create_jws_token(user_id: int, role: str, email: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "iss": ISSUER,
        "sub":str (user_id),
        "email": email,
        "exp": now + datetime.timedelta(minutes=60),
        "jti": str(uuid.uuid4()),
        "role": role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validate_jws_token(token: str):
    if token in token_blacklist:
        return None, "Token has been deleted (logout)"

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded, None
    except jwt.ExpiredSignatureError:
        token_blacklist[token] = "expired"
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

def add_to_blacklist(token: str):
    token_blacklist[token] = "blacklisted"
    return True



security = HTTPBearer()

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    token = res.credentials
    payload, error = validate_jws_token(token)

    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
