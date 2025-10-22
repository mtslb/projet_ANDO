from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

# Charger votre fichier CSV
df = pd.read_csv("procyclingstats.csv")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

weights = []

for idx, rider in enumerate(df["coureur"]):
    print(f"[{idx+1}/{len(df)}] Searching Wikipedia for {rider}...")
    
    search_url = f"https://en.wikipedia.org/w/index.php?search={rider.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(1.5)
    
    # Cliquer sur le premier résultat si on est sur la page de recherche
    try:
        first_result = driver.find_element(By.CSS_SELECTOR, "ul.mw-search-results li a")
        first_result.click()
        time.sleep(1)
    except:
        pass  # On est déjà sur la page
    
    poids = None
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        infobox = soup.find("table", class_="infobox")
        if infobox:
            # Chercher la ligne contenant "Weight"
            for row in infobox.find_all("tr"):
                header = row.find("th")
                if header and "weight" in header.get_text(strip=True).lower():
                    td = row.find("td")
                    if td:
                        text = td.get_text(" ", strip=True)
                        # Extraire le nombre en kg
                        match = re.search(r'(\d+)\s*kg', text)
                        if match:
                            poids = int(match.group(1))
                        else:
                            # Convertir si en lb
                            match_lb = re.search(r'(\d+)\s*lb', text)
                            if match_lb:
                                poids = round(int(match_lb.group(1)) * 0.453592)
                    break
    except Exception as e:
        print("Error:", e)

    weights.append(poids)
    print(f"→ {poids} kg")

driver.quit()

df["Weight_kg"] = weights
df.to_csv("wikipedia_with_weight.csv", index=False)
print("✅ Fichier généré : wikipedia_with_weight.csv")
