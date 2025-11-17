import os
import requests
import csv
from dotenv import load_dotenv

# Charger les variables depuis .env
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

CSV_FILE = "segments_strava.csv"

# Liste de segments à récupérer (id_strava, nom_optionnel)
SEGMENTS_KIGALI = [
    17412677,
    40168829,
    36137334,
    36137083,
    13673859,
    21629853
]

SEGMENTS = [
    1269095,
    17189607,
    37094861,
    36909346,
    617076,
    1228371
]

# 1️⃣ Rafraîchir le token
def refresh_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, data=payload)
    res.raise_for_status()
    data = res.json()
    access_token = data["access_token"]
    # mettre à jour le refresh_token si besoin
    new_refresh_token = data["refresh_token"]
    return access_token

# 2️⃣ Récupérer les infos d'un segment
def get_segment_info(segment_id, access_token):
    url = f"https://www.strava.com/api/v3/segments/{segment_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    segment_info = {
        "id_strava": data["id"],
        "nom": data["name"],
        "distance_m": data["distance"],
        "denivele_m": data["total_elevation_gain"],
        "pente_moy": data["average_grade"],
        "pente_max": data["maximum_grade"],
        "altitude_min": data["elevation_low"],
        "altitude_max": data["elevation_high"]
    }
    return segment_info

# 3️⃣ Écrire dans le CSV
def save_to_csv(segment_info, csv_file):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=segment_info.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(segment_info)
    print(f"✅ Segment {segment_info['nom']} ajouté au CSV")

# ──────────────
if __name__ == "__main__":
    try:
        token = refresh_access_token()
        for seg_id in SEGMENTS:
            info = get_segment_info(seg_id, token)
            save_to_csv(info, CSV_FILE)
    except requests.HTTPError as e:
        print("Erreur API :", e)
