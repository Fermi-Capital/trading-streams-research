import urllib.parse
import hashlib
import hmac
import base64
import json
import os

def get_kraken_signature(urlpath, data):
    key = os.getenv("KRAKEN_API_KEY")
    secret = os.getenv("KRAKEN_API_SECRET")
    if isinstance(data, str):
        encoded = (str(json.loads(data)["nonce"]) + data).encode()
    else:
        encoded = (str(data["nonce"]) + urllib.parse.urlencode(data)).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest()).decode()
    
    # construct the headers
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "API-Key": key,
        "API-Sign": sigdigest,
    }
