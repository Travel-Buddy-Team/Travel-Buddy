import os
import requests
from dotenv import load_dotenv
from opensky_auth import headers

load_dotenv()

URL = "https://opensky-network.org/api/states/all"
BOX = {"lamin": 37.0, "lamax": 38.0, "lomin": -123.0, "lomax": -122.0}


def check(label, **kwargs):
    r = requests.get(URL, params=BOX, timeout=30, **kwargs)
    remaining = r.headers.get("X-Rate-Limit-Remaining")
    print(f"{label:<14} status={r.status_code}  remaining={remaining}")
    return remaining


print("client id loaded:", os.getenv("OPENSKY_CLIENT_ID") is not None)

anon = check("anonymous")
auth = check("authenticated", headers=headers())

print()
if auth and int(auth) > 1000:
    print("Authenticated. Credits left today:", auth)
elif auth and anon and abs(int(anon) - int(auth)) <= 2:
    print("Still anonymous. token isn't being accepted.")
else:
    print("Check the status codes above.")