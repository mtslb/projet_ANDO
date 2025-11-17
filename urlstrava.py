import csv
import webbrowser
import urllib.parse
import unicodedata

# Nom du fichier CSV
csv_file = "wikipedia_with_height.csv"

base_url = "https://www.procyclingstats.com/rider/"

def remove_accents(input_str):
    """Supprime les accents d'une chaîne"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

start_line = 36  # Commencer à partir de la ligne 36
current_line = 0

with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        current_line += 1
        if current_line < start_line:
            continue  # Ignorer les lignes avant la ligne 36

        full_name = row[1].strip()  # Nom complet
        if full_name:
            parts = full_name.split()
            if len(parts) >= 2:
                prenom = remove_accents(parts[1])
                nom = remove_accents(parts[0])
                rider_name_for_url = f"{prenom}-{nom}".lower()
                rider_url = base_url + urllib.parse.quote(rider_name_for_url)
                webbrowser.open_new_tab(rider_url)
