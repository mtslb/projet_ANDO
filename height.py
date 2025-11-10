from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

# Charger le CSV avec les coureurs
df = pd.read_csv("wikipedia_with_weight.csv")

# Configurer Chrome headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

heights = []

for idx, rider in enumerate(df["coureur"]):
    print(f"[{idx+1}/{len(df)}] Searching Wikipedia for {rider}...")

    search_url = f"https://en.wikipedia.org/w/index.php?search={rider.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(1.5)

    # Si on est sur une page de résultats, cliquer sur le premier lien
    try:
        first_result = driver.find_element(By.CSS_SELECTOR, "ul.mw-search-results li a")
        first_result.click()
        time.sleep(1)
    except:
        pass

    height_m = None
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        infobox = soup.find("table", class_="infobox")
        if infobox:
            for row in infobox.find_all("tr"):
                header = row.find("th")
                if header and "height" in header.get_text(strip=True).lower():
                    td = row.find("td")
                    if td:
                        text = td.get_text(" ", strip=True).lower()
                        text = re.sub(r"\s+", " ", text)

                        # 1️⃣ Chercher le format mètre (ex: 1.75 m)
                        match_m = re.search(r"(\d+[.,]?\d*)\s?m", text)
                        if match_m:
                            val = float(match_m.group(1).replace(",", "."))
                            if 1.3 <= val <= 2.2:  # plage humaine réaliste
                                height_m = round(val, 2)
                                break

                        # 2️⃣ Sinon chercher le format centimètres (ex: 175 cm)
                        match_cm = re.search(r"(\d{2,3})\s?cm", text)
                        if match_cm:
                            val = int(match_cm.group(1))
                            if 130 <= val <= 220:
                                height_m = round(val / 100, 2)
                                break
    except Exception as e:
        print("Erreur:", e)

    heights.append(height_m)
    print(f"{rider} → {height_m} m")

driver.quit()

# Ajouter la colonne Height
df["Height_m"] = heights
df.to_csv("wikipedia_with_height.csv", index=False)
print("✅ Fichier généré : wikipedia_with_height.csv")
