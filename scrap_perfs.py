import os
import requests
import csv
from dotenv import load_dotenv

# ────────────── CONFIG ──────────────
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

SEGMENTS_FILE = "segments_strava.csv"          # CSV avec id_strava et nom
COUREURS_FILE = "wikipedia_with_height.csv"    # CSV de ta BDD de coureurs
OUTPUT_FILE = "segments_perfs.csv"            # CSV final avec les perfs filtrées

# ────────────── FONCTIONS ──────────────
def refresh_access_token():
    """Rafraîchir le token Strava avec le refresh token."""
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, data=payload)
    res.raise_for_status()
    return res.json()["access_token"]

def load_coureurs(csv_file):
    """Charger les noms des coureurs depuis le CSV et mettre en majuscule."""
    noms = set()
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            noms.add(row["coureur"].strip().upper())
    return noms

def load_segments(csv_file):
    """Charger les IDs et noms des segments depuis CSV."""
    segments = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append({
                "id_strava": int(row["id_strava"]),
                "nom": row["nom"]
            })
    return segments

def get_segment_leaderboard(segment_id, token):
    """Récupérer le leaderboard Strava pour un segment (limité aux segments accessibles)."""
    url = f"https://www.strava.com/api/v3/segments/{segment_id}/leaderboard"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 403:
        print(f"⚠️ Accès interdit au leaderboard {segment_id}")
        return []
    elif res.status_code != 200:
        print(f"⚠️ Erreur API {segment_id}: {res.status_code}")
        return []
    data = res.json()
    return data.get("entries", [])

def save_to_csv(rows, csv_file):
    """Sauvegarder les données filtrées dans un CSV."""
    if not rows:
        print("Aucune donnée à sauvegarder.")
        return
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"✅ Données sauvegardées dans {csv_file}")

# ────────────── MAIN ──────────────
if __name__ == "__main__":
    token = refresh_access_token()
    coureurs_bdd = load_coureurs(COUREURS_FILE)
    segments = load_segments(SEGMENTS_FILE)
    all_rows = []

    for seg in segments:
        leaderboard = get_segment_leaderboard(seg["id_strava"], token)
        for entry in leaderboard:
            athlete_name = entry.get("athlete_name", "").strip().upper()
            if athlete_name in coureurs_bdd:
                row = {
                    "id_strava": seg["id_strava"],
                    "segment_nom": seg["nom"],
                    "athlete_name": athlete_name,
                    "elapsed_time_s": entry.get("elapsed_time"),
                    "moving_time_s": entry.get("moving_time"),
                    "average_watts": entry.get("average_watts"),
                    "average_heartrate": entry.get("average_heartrate"),
                    "max_heartrate": entry.get("max_heartrate"),
                    "start_date": entry.get("start_date_local")
                }
                all_rows.append(row)
        print(f"✅ Segment {seg['nom']} traité, coureurs collectés: {len(all_rows)}")

    save_to_csv(all_rows, OUTPUT_FILE)
