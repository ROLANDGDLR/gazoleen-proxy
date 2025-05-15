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

    simplified = []
    for rdv in data:
        simplified.append({
            "id": rdv.get("id"),
            "client": rdv.get("clientNom") or rdv.get("client", {}).get("nom"),
            "adresse": rdv.get("adresse") or rdv.get("client", {}).get("adresse"),
            "ville": rdv.get("ville") or rdv.get("client", {}).get("ville"),
            "technicien": rdv.get("intervenantNom") or rdv.get("intervenant", {}).get("nom"),
            "heure_debut": rdv.get("heureDebut"),
            "heure_fin": rdv.get("heureFin"),
            "objet": rdv.get("titre") or rdv.get("typeIntervention"),
            "statut": rdv.get("statut"),
            "temps_prevu": rdv.get("tempsPrevu"),
            "type": rdv.get("typeIntervention")
        })

    return simplified
