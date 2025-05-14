from fastapi import FastAPI
import hashlib
import datetime
import requests

app = FastAPI()

APIKEY = "6791ca581758ccaf6486f4dd100c1f24e6c1eff4"     
REFADMIN = "75"

def get_token():
    date = datetime.datetime.now().strftime("%Y%m%d")
    token_input = date + REFADMIN + APIKEY
    return hashlib.sha1(token_input.encode()).hexdigest()

@app.get("/planning")
def planning(date: str):
    token = get_token()
    url = f"https://ramonetou.gazoleen.com/ws/meetings/{date}?t={token}-{REFADMIN}"
    response = requests.get(url)
    return response.json()