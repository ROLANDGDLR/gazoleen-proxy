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

def extract_cp(adresse):
    if not adresse:
        return None
    match = re.search(r"\b\d{5}\b", adresse)
    return match.group() if match else None

def parse_duree(duree_str):
    if not isinstance(duree_str, str):
        return 0
    match = re.match(r"(?:(\d+)h)?(?:(\d+)min|\d+)?", duree_str.replace(" ", "").replace("mn", "min"))
    if not match:
        return 0
    heures = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return heures * 60 + minutes

def get_max_day_minutes():
    # Matin : 8h30-13h30 (5h) = 300min / AM : 14h-18h30 (4h30) = 270min
    return 300 + 270

@app.get("/planning")
def planning(date: str):
    token = get_token()
    url = f"https://ramonetou.gazoleen.com/ws/meetings/{date}?t={token}-{REFADMIN}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "Erreur lors de l'appel à Gazoleen", "status_code": response.status_code}

    data = response.json()
    result = []
    charge_par_tech = {}
    max_day_minutes = get_max_day_minutes()

    for bloc in data:
        technicien = bloc.get("name")
        date_rdv = bloc.get("date")
        total_minutes = 0

        for meeting in bloc.get("meetings", []):
            client = meeting.get("client", {})
            services = meeting.get("services")
            if not services or not isinstance(services, list):
                services = [{}]
            service = services[0]

            duree_txt = service.get("duration", "0h00")
            duree_min = parse_duree(duree_txt)
            total_minutes += duree_min

            result.append({
                "technicien": technicien,
                "date": date_rdv,
                "heure": meeting.get("time"),
                "client": client.get("name"),
                "adresse": client.get("address"),
                "code_postal": extract_cp(client.get("address")),
                "telephone": client.get("phone1"),
                "objet": service.get("label"),
                "duree": duree_txt
            })

        if technicien:
            charge_par_tech[technicien] = charge_par_tech.get(technicien, 0) + total_minutes

    return {
        "rendez_vous": result,
        "charge": [
            {
                "technicien": tech,
                "temps_occupe_min": charge,
                "temps_max_min": max_day_minutes,
                "temps_restant_min": max_day_minutes - charge
            } for tech, charge in charge_par_tech.items()
        ]
    }
