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

    if response.status_code != 200:
        return {"error": "Erreur lors de l'appel à Gazoleen", "status_code": response.status_code}

    data = response.json()
    result = []

    for bloc in data:
        technicien = bloc.get("name")
        date_rdv = bloc.get("date")
        for meeting in bloc.get("meetings", []):
            client = meeting.get("client", {})
            service = meeting.get("services", [{}])[0]

            result.append({
                "technicien": technicien,
                "date": date_rdv,
                "heure": meeting.get("time"),
                "client": client.get("name"),
                "adresse": client.get("address"),
                "telephone": client.get("phone1"),
                "objet": service.get("label"),
                "duree": service.get("duration")
            })

    return result
