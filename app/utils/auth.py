import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/blog-api/auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ISSUER = os.getenv("ISSUER")
AUDIENCE = os.getenv("AUDIENCE")


def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin user"""
    return username == ADMIN_USERNAME and pwd_context.verify(password, ADMIN_PASSWORD_HASH)

def create_access_token(username: str) -> str:
    """Create a JWT access token"""
    now = datetime.now(timezone.utc)
    data = {
        "sub": username,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now,
        "nbf": now,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "jti": str(uuid4())
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_admin(token: str = Depends(oauth2_scheme)):
    """Verify JWT token and return username"""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE
        )
        username: str = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")
