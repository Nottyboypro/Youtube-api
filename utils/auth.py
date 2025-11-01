import bcrypt
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config import SECRET_KEY_JWT
from database import mongo
from logging_ import LOGGER

logger = LOGGER(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

def hash_api_key_raw(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_api_key_hash(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

def create_admin_jwt(data: dict, expires_minutes: int = 60*24):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY_JWT, algorithm="HS256")

async def admin_auth_dependency(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid admin token")

# API key validation and atomic increment
async def verify_api_key_and_consume(raw_key: str):
    # raw_key expected to begin with NottyBoy-
    if not raw_key.startswith("NottyBoy-"):
        return None
    # find candidate keys and verify by verifying hash
    cursor = mongo.mongodb.api_keys.find({})
    async for doc in cursor:
        if verify_api_key_hash(raw_key, doc["api_key_hash"]):
            # check status
            if doc.get("status") != "active": 
                return None
            if doc.get("expiry_date") and doc["expiry_date"] < datetime.utcnow():
                return None
            # atomically increase used_today if limit not reached
            res = await mongo.mongodb.api_keys.find_one_and_update(
                {"_id": doc["_id"], "used_today": {"$lt": doc["daily_limit"]}},
                {"$inc": {"used_today": 1}},
                return_document=True
            )
            if res:
                return res
            else:
                return None
    return None
