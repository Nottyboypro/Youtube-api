from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from utils.keygen import generate_api_key
from utils.auth import create_admin_jwt, admin_auth_dependency, hash_api_key_raw
from database import mongo
from logging_ import LOGGER

admin_router = APIRouter()
logger = LOGGER(__name__)

class LoginIn(BaseModel):
    username: str
    password: str

class CreateKeyIn(BaseModel):
    owner: str
    daily_limit: int = 5000
    expiry_days: int = 30

@admin_router.post("/login")
async def login(payload: LoginIn):
    # simple admin check using env credentials
    from config import ADMIN_USERNAME, ADMIN_PASSWORD
    if payload.username != ADMIN_USERNAME or payload.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_admin_jwt({"sub": payload.username})
    return {"access_token": token, "token_type": "bearer"}

@admin_router.post("/create_key")
async def create_key(payload: CreateKeyIn, admin=Depends(admin_auth_dependency)):
    raw = generate_api_key(payload.owner)
    hashed = hash_api_key_raw(raw)
    doc = {
        "owner": payload.owner,
        "api_key_hash": hashed,
        "daily_limit": payload.daily_limit,
        "used_today": 0,
        "expiry_date": datetime.utcnow() + timedelta(days=payload.expiry_days),
        "created_at": datetime.utcnow(),
        "status": "active"
    }
    await mongo.mongodb.api_keys.insert_one(doc)
    # return raw key only once
    return {"api_key": raw, "owner": payload.owner, "expiry_date": doc["expiry_date"].isoformat()}

@admin_router.get("/list_keys")
async def list_keys(admin=Depends(admin_auth_dependency)):
    keys = []
    cursor = mongo.mongodb.api_keys.find({}, {"api_key_hash": 0})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        keys.append(doc)
    return {"keys": keys}

@admin_router.post("/reset_limits")
async def reset_limits(admin=Depends(admin_auth_dependency)):
    res = await mongo.mongodb.api_keys.update_many({}, {"$set": {"used_today": 0}})
    return {"modified_count": res.modified_count}
