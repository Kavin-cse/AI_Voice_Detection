import os
from fastapi import Header, HTTPException

# Default to a development API key if none is set. In production, set a strong API_KEY in the environment.
API_KEY = os.getenv('API_KEY', 'testkey')

def validate_api_key(x_api_key: str | None):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail='Missing API key')
    if API_KEY is None:
        raise HTTPException(status_code=500, detail='Server misconfiguration: API key not set')
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API key')
    return True
