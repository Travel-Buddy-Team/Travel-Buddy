import os, time, requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = ("https://auth.opensky-network.org/auth/realms/"
             "opensky-network/protocol/openid-connect/token")

_cache = {"token": None, "expires": 0.0}


def get_token():
    if _cache["token"] and time.time() < _cache["expires"]:
        return _cache["token"]
    r = requests.post(TOKEN_URL, timeout=30, data={
        "grant_type": "client_credentials",
        "client_id": os.getenv("OPENSKY_CLIENT_ID"),
        "client_secret": os.getenv("OPENSKY_CLIENT_SECRET"),
    })
    r.raise_for_status()
    j = r.json()
    _cache["token"] = j["access_token"]
    _cache["expires"] = time.time() + j.get("expires_in", 1800) - 30
    return _cache["token"]


def headers():
    return {"Authorization": f"Bearer {get_token()}"}